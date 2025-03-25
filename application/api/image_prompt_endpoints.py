import logging
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile
from starlette.responses import Response, StreamingResponse

from application.dependencies import get_metagraph_manager, verify_api_key
from application.prompt_manager.image_prompt_manager import image_prompt_manager
from application.utils.image_serializer import image_prompt_serializer
from application.utils.metagraph_manager import MetagraphManager
from application.utils.schemas.metagraph_data import MetagraphData


_logger = logging.getLogger("uvicorn")


image_prompt_router = APIRouter(tags=["Image Prompts"])


@image_prompt_router.post(
    path="/download",
    summary="Download batch of image prompts in messagepack format.",
    description="Download batch of image prompts in messagepack format. "
    "Each message is sent in format {'normalized_prompt': '...', 'data': '...'}",
)
async def download_image_prompt_batch(
    request: MetagraphData,
    metagraph_manager: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> StreamingResponse:
    metagraph_manager.verify_signature(request.hotkey, request.nonce, request.signature)
    normalized_prompt = f"{datetime.now().timestamp()}.msgpack"
    batch = await image_prompt_manager.get_batch()

    _logger.info(f"Returning {normalized_prompt}...")

    return StreamingResponse(
        image_prompt_serializer.serialize(image_prompts=batch),
        media_type="application/x-msgpack",
        headers={"Content-Disposition": f"attachment; normalized_prompt={normalized_prompt}"},
    )


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts in message pack format.",
    description="Submit batch of image prompts in message pack format. "
    "Messages should be sent as bytes stream"
    " in format {'normalized_prompt': '...', 'data': '...'}",
)
async def upload_image_prompt_batch(
    file: UploadFile,
    api_key: str = Depends(verify_api_key),  # noqa: B008
) -> Response:
    await image_prompt_serializer.deserialize(file=file)
    await file.close()
    return Response(status_code=200)
