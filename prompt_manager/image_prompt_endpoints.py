from collections.abc import AsyncGenerator
from datetime import datetime
from io import BytesIO
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from main.dependencies import get_metagraph_manager, verify_api_key
from main.schemas.metagraph_data import MetagraphData
from starlette.responses import Response, StreamingResponse
from utils.archive_manager import ZipArchiveManager
from utils.metagraph_manager import MetagraphManager

from prompt_manager.image_prompt_manager import image_prompt_manager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


image_prompt_router = APIRouter(tags=["Image Prompts"])

_CHUNK_SIZE: int = 1024 * 1024


@image_prompt_router.post(
    path="/download",
    summary="Download batch of image prompts.",
)
async def download_prompt_batch(
    request: MetagraphData,
    background_tasks: BackgroundTasks,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> StreamingResponse:
    metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = await image_prompt_manager.get_batch()
    zip_data = await ZipArchiveManager.compress(image_prompts=batch.image_prompts)

    async def file_stream(zip_data: BytesIO) -> AsyncGenerator[bytes, Any]:
        while chunk := zip_data.read(_CHUNK_SIZE):
            yield chunk
        zip_data.close()

    background_tasks.add_task(zip_data.close)

    return StreamingResponse(
        file_stream(zip_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={datetime.now().timestamp()}.zip"},
    )


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts in zip format.",
)
async def upload_file(
    background_tasks: BackgroundTasks, file: UploadFile, api_key: str = Depends(verify_api_key)  # noqa: B008
) -> Response:
    # todo Check that it is a zip archive
    zip_data = BytesIO()
    while chunk := await file.read(_CHUNK_SIZE):
        zip_data.write(chunk)
    zip_data.seek(0)

    async def add_images(data: BytesIO) -> None:
        image_prompts = await ZipArchiveManager.decompress(zip_data=data)
        image_prompt_manager.submit(image_batch=ImagePromptBatch(image_prompts=image_prompts))
        data.close()

    background_tasks.add_task(add_images, zip_data)
    return Response(status_code=200)
