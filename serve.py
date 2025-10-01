import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from metagraph.config import read_config
from metagraph.sync_metagraph import sync_metagraph_cron, sync_metagraph
from api.dependencies import get_metagraph, verify_api_key, get_text_prompt_storage
from exceptions import (
    BaseException,
    InvalidApiKeyException,
    InvalidSignatureException,
    NotEnoughPromptsAvailable,
)
from api.image_prompt_endpoints import image_prompt_router
from metagraph.metagraph import Metagraph
from api.models import MetagraphData
from prompt_storage import PromptStorage
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
    # Sync metagraph first time
    await sync_metagraph()
    # Start sync metagraph cron
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


@app.get("/health")
async def health() -> str:
    return "OK"


if __name__ == "__main__":
    from settings import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.port)  # noqa: S104
