from fastapi import APIRouter, Depends

from api.dependencies import get_metagraph, verify_api_key
from metagraph.metagraph import Metagraph
from api.models import MetagraphDataDTO, TextPromptDTO
from prompt_storage.text_prompt_storage import TextPromptStorage
from api.dependencies import get_text_prompt_storage


text_prompt_router = APIRouter(tags=["Text Prompts"])


@text_prompt_router.post(path="/submit", summary="Submit text prompts")
async def submit_strings(
    request: TextPromptDTO, 
    api_key: str = Depends(verify_api_key),
    text_prompt_storage: TextPromptStorage = Depends(get_text_prompt_storage),
) -> None:  # noqa: B008
    text_prompt_storage.add(prompts=request.normalized_prompts)


@text_prompt_router.post(path="/batch", summary="Fetch batch of text prompts")
async def get_text_prompt_batch(
    request: MetagraphDataDTO,
    text_prompt_storage: TextPromptStorage = Depends(get_text_prompt_storage),
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> TextPromptDTO:
    metagraph.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_storage.get_batch()
    return TextPromptDTO(normalized_prompts=batch)
