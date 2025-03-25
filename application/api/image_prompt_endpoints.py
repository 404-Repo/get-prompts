import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from starlette.responses import Response, StreamingResponse

from application.dependencies import get_metagraph_manager
from application.prompt_manager.image_prompt_manager import image_prompt_manager
from application.prompt_manager.schemas.prompt_batch import ImagePromptBatch
from application.utils.image_serializer import image_prompt_serializer
from application.utils.metagraph_manager import MetagraphManager


_logger = logging.getLogger("uvicorn")


image_prompt_router = APIRouter(tags=["Image Prompts"])

_CHUNK_SIZE: int = 1024 * 1024


@image_prompt_router.get(
    path="/download",
    summary="Download batch of image prompts.",
)
async def download_prompt_batch(
    # request: MetagraphData,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> StreamingResponse:
    # metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    filename = f"{datetime.now().timestamp()}.msgpack"
    batch = await image_prompt_manager.get_batch()

    _logger.info(f"Returning {filename}...")

    return StreamingResponse(
        image_prompt_serializer.serialize(image_prompts=batch.image_prompts),
        media_type="application/x-msgpack",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts in zip format.",
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    # api_key: str = Depends(verify_api_key),  # noqa: B008
) -> Response:
    _logger.info(f"Uploading {file.filename} to memory.")
    image_prompts = await image_prompt_serializer.deserialize(file=file)
    await file.close()
    _logger.info(f"{len(image_prompts)} image prompts were uploaded.")
    background_tasks.add_task(image_prompt_manager.submit, image_batch=ImagePromptBatch(image_prompts=image_prompts))
    return Response(status_code=200)
