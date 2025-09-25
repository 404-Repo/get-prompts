import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from metagraph.config import read_config
from metagraph.sync_metagraph import sync_metagraph_cron
from api.dependencies import get_metagraph, verify_api_key, get_text_prompt_storage
from exceptions import (
    BaseException,
    InvalidApiKeyException,
    InvalidSignatureException,
    NotEnoughPromptsAvailable,
)
from api.image_prompt_endpoints import image_prompt_router
from metagraph.metagraph import Metagraph
from api.models import MetagraphDataDTO
from prompt_storage.text_prompt_storage import TextPromptStorage
from api.text_prompt_endpoints import text_prompt_router
from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_200_OK


_logger = logging.getLogger("uvicorn")
config = read_config()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    _logger.info(config)
    asyncio.create_task(sync_metagraph_cron())
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(image_prompt_router, prefix="/image-prompts")
app.include_router(text_prompt_router, prefix="/text-prompts")


@app.exception_handler(BaseException)
async def custom_exception_handler(request: Request, exc: BaseException) -> JSONResponse:
    if isinstance(exc, InvalidSignatureException):
        return JSONResponse(status_code=403, content={"error": "Signature error", "message": str(exc)})
    elif isinstance(exc, InvalidApiKeyException):
        return JSONResponse(status_code=403, content={"error": "Invalid API key", "message": str(exc)})
    elif isinstance(exc, NotEnoughPromptsAvailable):
        return JSONResponse(status_code=400, content={"error": "Not enough prompts available", "message": str(exc)})
    return JSONResponse(status_code=500, content={"error": "Unhandled Exception", "message": str(exc)})


# todo: remove because deprecated
@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(
    batch: list[str], 
    api_key: str = Depends(verify_api_key), 
    text_prompt_storage: TextPromptStorage = Depends(get_text_prompt_storage)
) -> Response:  # noqa: B008
    text_prompt_storage.add(prompts=batch)
    return Response()


# todo: remove because deprecated
@app.post("/get")
async def get_strings(
    request: MetagraphDataDTO,
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
    text_prompt_storage: TextPromptStorage = Depends(get_text_prompt_storage),
) -> list[str]:
    metagraph.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_storage.get_batch()
    return batch


if __name__ == "__main__":
    from settings import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.port)  # noqa: S104
