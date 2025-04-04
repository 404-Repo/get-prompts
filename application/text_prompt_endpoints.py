from fastapi import APIRouter, Depends

from application.config import config
from application.dependencies import get_metagraph, verify_api_key
from application.metagraph import Metagraph
from application.models import MetagraphDataDTO, TextPromptDTO
from application.prompt.text_prompt import text_prompt


text_prompt_router = APIRouter(tags=["Text Prompts"])


@text_prompt_router.post(path="/submit", summary="Submit text prompts")
async def submit_strings(request: TextPromptDTO, api_key: str = Depends(verify_api_key)) -> None:  # noqa: B008
    text_prompt.submit(prompts=request.normalized_prompts)


@text_prompt_router.post(path="/batch", summary="Fetch batch of text prompts")
async def get_text_prompt_batch(
    request: MetagraphDataDTO,
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> list[str]:
    metagraph.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt.get_batch(batch_size=config.text_prompt_batch_size)
    return batch
