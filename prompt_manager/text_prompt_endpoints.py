from fastapi import APIRouter, Depends
from main.dependencies import get_metagraph_manager, verify_api_key
from main.schemas.metagraph_data import MetagraphData
from starlette.responses import Response
from starlette.status import HTTP_200_OK
from utils.metagraph_manager import MetagraphManager

from prompt_manager.schemas.prompt_batch import BasePromptBatch, TextPromptBatch
from prompt_manager.text_prompt_manager import text_prompt_manager


text_prompt_router = APIRouter(tags=["Text Prompts"])


@text_prompt_router.post(
    path="/submit", status_code=HTTP_200_OK, summary="Submit text prompts", response_class=Response
)
async def submit_strings(batch: TextPromptBatch, api_key: str = Depends(verify_api_key)) -> Response:  # noqa: B008
    text_prompt_manager.submit(batch=TextPromptBatch(prompts=batch.prompts))
    return Response()


@text_prompt_router.post(path="/fetch-batch", summary="Fetch a batch of text prompts", response_model=TextPromptBatch)
async def fetch_text_prompt_batch(
    request: MetagraphData,
    metagraph: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> BasePromptBatch:
    metagraph.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_manager.get()
    return batch
