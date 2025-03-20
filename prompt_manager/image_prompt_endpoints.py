from collections.abc import AsyncGenerator
from pathlib import Path

import aiofiles  # type: ignore
from fastapi import APIRouter, BackgroundTasks, UploadFile
from starlette.responses import Response, StreamingResponse

from prompt_manager.image_prompt_manager import image_prompt_manager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


image_prompt_router = APIRouter(tags=["Image Prompts"])

_CHUNK_SIZE: int = 1024 * 1024


@image_prompt_router.get(
    path="/download",
    summary="Download batch of image prompts.",
)
async def download_prompt_batch(
    # request: MetagraphData,
    # metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> StreamingResponse:
    # if not metagraph.verify_signature(request.hotkey, request.nonce, request.signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature provided.")

    batch = await image_prompt_manager.get()

    async def iterfile() -> AsyncGenerator[bytes, None]:
        async with aiofiles.open(batch.archive_path, "rb") as f:
            while chunk := await f.read(_CHUNK_SIZE):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={batch.archive_path}"},
    )


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts.",
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
) -> Response:
    async def save_file(file: UploadFile, archive_path: Path) -> None:
        async with aiofiles.open(archive_path, "wb") as out_file:
            while chunk := await file.read(_CHUNK_SIZE):
                await out_file.write(chunk)

    archive_path = image_prompt_manager.get_archive_path()
    await save_file(file, archive_path)
    background_tasks.add_task(image_prompt_manager.submit, batch=ImagePromptBatch(archive_path=archive_path))
    return Response(status_code=200)
