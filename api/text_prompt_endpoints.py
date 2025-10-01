from fastapi import APIRouter, Depends

from api.dependencies import get_metagraph, verify_api_key
from metagraph.metagraph import Metagraph
from api.models import GetPromptsRequest, GetPromptsResponse, SubmitPromptsRequest
from prompt_storage import PromptStorage
from api.dependencies import get_text_prompt_storage


text_prompt_router = APIRouter(tags=["Text Prompts"])


@text_prompt_router.post(path="/submit", summary="Submit text prompts")
async def submit_strings(
    request: SubmitPromptsRequest, 
    api_key: str = Depends(verify_api_key),
    text_prompt_storage: PromptStorage = Depends(get_text_prompt_storage),
) -> None:  # noqa: B008
    text_prompt_storage.add(prompts=request.prompts)


@text_prompt_router.post(path="/get", summary="Fetch batch of text prompts")
async def get_text_prompt_batch(
    request_data: GetPromptsRequest,
    text_prompt_storage: PromptStorage = Depends(get_text_prompt_storage),
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> GetPromptsResponse:
    metagraph.verify_signature(request_data.hotkey, request_data.nonce, request_data.signature)
    batch = text_prompt_storage.get_batch()
    return GetPromptsResponse(prompts=batch)
