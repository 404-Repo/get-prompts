import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_200_OK

from application.api.image_prompt_endpoints import image_prompt_router
from application.api.text_prompt_endpoints import text_prompt_router
from application.config import config
from application.cron import sync_metagraph_cron
from application.dependencies import get_metagraph_manager, verify_api_key
from application.exceptions import BaseException, InvalidApiKeyException, InvalidSignatureException, NotEnoughImages
from application.prompt_manager.text_prompt_manager import text_prompt_manager
from application.utils.metagraph_manager import MetagraphManager
from application.utils.schemas.metagraph_data import MetagraphData


_logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    _logger.info(config)
    asyncio.create_task(sync_metagraph_cron())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(image_prompt_router, prefix="/images")
app.include_router(text_prompt_router, prefix="/texts")


@app.exception_handler(BaseException)
async def custom_exception_handler(request: Request, exc: BaseException) -> JSONResponse:
    if isinstance(exc, InvalidSignatureException):
        return JSONResponse(status_code=403, content={"error": "Signature error", "message": str(exc)})
    elif isinstance(exc, InvalidApiKeyException):
        return JSONResponse(  # 🛠 Fixed: Added missing `return`
            status_code=403, content={"error": "Invalid API key", "message": str(exc)}
        )
    elif isinstance(exc, NotEnoughImages):
        return JSONResponse(  # 🛠 Fixed: Added missing `return`
            status_code=400, content={"error": "Not enough images", "message": str(exc)}
        )

    return JSONResponse(status_code=500, content={"error": "Unhandled Exception", "message": str(exc)})


# todo: remove because deprecated
@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(batch: list[str], api_key: str = Depends(verify_api_key)) -> Response:  # noqa: B008
    text_prompt_manager.submit(batch=batch)
    return Response()


# todo: remove because deprecated
@app.post("/get")
async def get_strings(
    request: MetagraphData,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> list[str]:
    metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_manager.get_batch()
    return batch


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)  # noqa: S104
