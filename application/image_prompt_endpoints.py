import logging
from typing import cast

from fastapi import APIRouter, Depends, Query
from pydantic import HttpUrl

from application.config import config
from application.dependencies import get_metagraph, verify_api_key
from application.metagraph import Metagraph
from application.models import ImagePromptObtainDTO, ImagePromptPartial, ImagePromptSubmitDTO, MetagraphDataDTO
from application.prompt.image_prompt import image_prompt


_logger = logging.getLogger("uvicorn")


image_prompt_router = APIRouter(tags=["Image Prompts"])


@image_prompt_router.post(
    path="/batch",
    summary="Obtain batch of image prompts with optional normalized text prompts.",
    description="Obtain batch of image prompt image_prompts with optional normalized text prompt.",
    response_model=ImagePromptObtainDTO,
)
async def obtain_image_prompt_batch(
    metagraph_data: MetagraphDataDTO,
    include_normalized_prompt: bool = Query(default=False, help="Include normalized prompts."),
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> ImagePromptObtainDTO:
    metagraph.verify_signature(metagraph_data.hotkey, metagraph_data.nonce, metagraph_data.signature)
    batch = image_prompt.get_batch(batch_size=config.image_prompt_batch_size)
    return ImagePromptObtainDTO(
        prompts=[
            ImagePromptPartial(
                url=cast(HttpUrl, url),
                normalized_prompt=prompt if include_normalized_prompt else None,
            )
            for url, prompt in batch.items()
        ]
    )


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts.",
    description="Submit batch of image prompts optionally containing normalized text prompts.",
)
async def submit_image_prompt_batch(
    request: ImagePromptSubmitDTO,
    api_key: str = Depends(verify_api_key),  # noqa: B008
) -> None:
    image_prompt.submit(batch={str(prompt.url): prompt.normalized_prompt for prompt in request.prompts})
