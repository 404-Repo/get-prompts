import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_200_OK

from application.api.image_prompt_endpoints import image_prompt_router
from application.api.text_prompt_endpoints import text_prompt_router
from application.config import config
from application.cron.check_ram_job import CheckRAMJob
from application.cron.cron_scheduler import CronScheduler
from application.cron.sync_metagraph_job import SyncMetagraphJob
from application.dependencies import get_metagraph_manager, verify_api_key
from application.exceptions import BaseException, InvalidApiKeyException, InvalidSignatureException, NotEnoughImages
from application.prompt_manager.schemas.prompt_batch import BasePromptBatch, TextPromptBatch
from application.prompt_manager.text_prompt_manager import text_prompt_manager
from application.utils.metagraph_manager import MetagraphManager
from application.utils.schemas.metagraph_data import MetagraphData


_logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    next_run_time = datetime.now(UTC) + timedelta(seconds=1)

    CronScheduler.add_job(
        job_type=CheckRAMJob,
        id="check_ram_cron_job",
        trigger="interval",
        minutes=1,
        next_run_time=next_run_time,
        misfire_grace_time=60,
    )
    CronScheduler.add_job(
        job_type=SyncMetagraphJob,
        id="sync_metagraph_cron_job",
        trigger="interval",
        minutes=30,
        next_run_time=next_run_time,
        misfire_grace_time=60,
    )
    CronScheduler.start()

    _logger.info(config)
    yield
    CronScheduler.shutdown()


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
async def submit_strings(batch: TextPromptBatch, api_key: str = Depends(verify_api_key)) -> Response:  # noqa: B008
    text_prompt_manager.submit(batch=TextPromptBatch(prompts=batch.prompts))
    return Response()


# todo: remove because deprecated
@app.post("/get", response_model=TextPromptBatch)
async def get_strings(
    request: MetagraphData,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> BasePromptBatch:
    metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_manager.get_batch()
    return batch


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)  # noqa: S104
