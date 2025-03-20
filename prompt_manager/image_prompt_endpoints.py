from collections.abc import AsyncGenerator

import aiofiles  # type: ignore
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from prompt_manager.image_prompt_manager import image_prompt_manager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


image_prompt_router = APIRouter(tags=["Image Prompts"])


@image_prompt_router.get(
    path="/download",
    summary="Download batch of image prompts.",
    response_model=ImagePromptBatch,
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
            while chunk := await f.read(1024 * 1024):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={batch.archive_path}"},
    )
