from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from config import config
from fastapi import Depends, FastAPI
from prompt_manager.image_prompt_endpoints import image_prompt_router
from prompt_manager.schemas.prompt_batch import BasePromptBatch, TextPromptBatch
from prompt_manager.text_prompt_endpoints import text_prompt_router
from prompt_manager.text_prompt_manager import text_prompt_manager
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_200_OK
from utils.metagraph_manager import MetagraphManager

from main.dependencies import get_metagraph_manager, verify_api_key
from main.exceptions import BaseException, InvalidApiKeyException, InvalidSignatureException
from main.schemas.metagraph_data import MetagraphData


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    print(config)
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

    return JSONResponse(status_code=500, content={"error": "Unhandled Exception", "message": str(exc)})


# todo: remove because deprecated
@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(batch: TextPromptBatch, api_key: str = Depends(verify_api_key)) -> Response:  # noqa: B008
    text_prompt_manager.submit(batch=TextPromptBatch(prompts=batch.prompts))
    return Response()


# todo: remove because deprecated
@app.get("/get", response_model=TextPromptBatch)
async def get_strings(
    request: MetagraphData,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> BasePromptBatch:
    metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_manager.get()
    return batch


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)  # noqa: S104
