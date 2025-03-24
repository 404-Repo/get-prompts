from collections.abc import AsyncGenerator
from datetime import datetime
from io import BytesIO
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from main.dependencies import get_metagraph_manager
from starlette.responses import Response, StreamingResponse
from utils.metagraph_manager import MetagraphManager

from prompt_manager.image_prompt_manager import image_prompt_manager


image_prompt_router = APIRouter(tags=["Image Prompts"])

_CHUNK_SIZE: int = 1024 * 1024


@image_prompt_router.post(
    path="/download",
    summary="Download batch of image prompts.",
)
async def download_prompt_batch(
    # request: MetagraphData,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> StreamingResponse:
    # metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    filename = f"{datetime.now().timestamp()}.zip"
    print(f"Creating batch for {filename}")
    # batch = await image_prompt_manager.get_batch()
    print(f"Batch created for {filename}")
    print(f"Compressing {filename}")

    async def file_stream(zip_data: BytesIO) -> AsyncGenerator[bytes, Any]:
        try:
            while chunk := zip_data.read(_CHUNK_SIZE):
                yield chunk
        finally:
            zip_data.close()

    # background_tasks.add_task(zip_data.close)
    print(f"Returning {filename}...")

    return StreamingResponse(
        file_stream(zip_data),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts in zip format.",
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., max_length=500 * 1024 * 1024),  # api_key: str = Depends(verify_api_key)  # noqa: B008
) -> Response:
    # # todo Check that it is a zip archive
    # print(f"Uploading file {file.filename}")
    # zip_data = BytesIO()
    # while chunk := await file.read(_CHUNK_SIZE):
    #     zip_data.write(chunk)
    # zip_data.seek(0)
    # print(f"File successfully uploaded in memory")
    #
    # async def add_images(data: BytesIO) -> None:
    #     try:
    #         print(f"Extracting images from {file.filename}")
    #         print(f"{len(image_prompts)} images were extracted.")
    #         image_prompt_manager.submit(image_batch=ImagePromptBatch(image_prompts=image_prompts))
    #         print(f"{len(image_prompt_manager._submitted_image_storage._image_prompts)} now in RAM")
    #     finally:
    #         data.close()
    #
    # background_tasks.add_task(add_images, zip_data)
    return Response(status_code=200)
