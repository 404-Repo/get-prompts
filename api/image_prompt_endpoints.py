import logging
from typing import cast

from fastapi import APIRouter, Depends
from pydantic import HttpUrl

from api.dependencies import get_metagraph, verify_api_key
from metagraph.metagraph import Metagraph   
from api.models import ImagePromptObtainDTO, ImagePromptSubmitDTO, MetagraphDataDTO
from prompt_storage.image_prompt_storage import ImagePromptStorage
from api.dependencies import get_image_prompt_storage
from prompt_storage.image_prompt import ImagePrompt

_logger = logging.getLogger("uvicorn")


image_prompt_router = APIRouter(tags=["Image Prompts"])


@image_prompt_router.post(
    path="/batch",
    summary="Obtain batch of image prompts with optional normalized text prompts.",
    description="Obtain batch of image prompts with optional normalized text prompts.",
    response_model=ImagePromptObtainDTO,
)
async def obtain_image_prompt_batch(
    metagraph_data: MetagraphDataDTO,
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
    image_prompt_storage: ImagePromptStorage = Depends(get_image_prompt_storage),
) -> ImagePromptObtainDTO:
    metagraph.verify_signature(metagraph_data.hotkey, metagraph_data.nonce, metagraph_data.signature)
    batch = image_prompt_storage.get_batch()
    return ImagePromptObtainDTO(prompts=batch)


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts.",
    description="Submit batch of image prompts containing normalized text prompts.",
)
async def submit_image_prompt_batch(
    request: ImagePromptSubmitDTO,
    api_key: str = Depends(verify_api_key),  # noqa: B008
    image_prompt_storage: ImagePromptStorage = Depends(get_image_prompt_storage),
) -> None:
    image_prompt_storage.add(prompts=request.prompts)
