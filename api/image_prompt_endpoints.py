import logging
from typing import cast

from fastapi import APIRouter, Depends
from pydantic import HttpUrl

from api.dependencies import get_metagraph, verify_api_key
from metagraph.metagraph import Metagraph   
from api.models import GetPromptsResponse, SubmitPromptsRequest, GetPromptsRequest
from prompt_storage import PromptStorage
from api.dependencies import get_image_prompt_storage


_logger = logging.getLogger("uvicorn")


image_prompt_router = APIRouter(tags=["Image Prompts"])


@image_prompt_router.post(
    path="/get",
    description="Get batch of image prompts with optional normalized text prompts.",
    response_model=GetPromptsResponse,
)
async def get_image_prompt_batch(
    request_data: GetPromptsRequest,
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
    image_prompt_storage: PromptStorage = Depends(get_image_prompt_storage),
) -> GetPromptsResponse:
    metagraph.verify_signature(request_data.hotkey, request_data.nonce, request_data.signature)
    batch = image_prompt_storage.get_batch()
    return GetPromptsResponse(prompts=batch)


@image_prompt_router.post(
    path="/submit",
    summary="Submit batch of image prompts.",
    description="Submit batch of image prompts containing normalized text prompts.",
)
async def submit_image_prompt_batch(
    request: SubmitPromptsRequest,
    api_key: str = Depends(verify_api_key),  # noqa: B008
    image_prompt_storage: PromptStorage = Depends(get_image_prompt_storage),
) -> None:
    image_prompt_storage.add(prompts=request.prompts)
