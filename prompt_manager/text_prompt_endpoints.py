from fastapi import APIRouter, Depends, HTTPException
from main.dependencies import get_metagraph_manager, verify_api_key
from main.schemas.metagraph_data import MetagraphData
from starlette.responses import Response
from starlette.status import HTTP_200_OK
from utils.metagraph_manager import MetagraphManager

from prompt_manager.schemas.prompt_batch import BasePromptBatch, TextPromptBatch
from prompt_manager.text_prompt_manager import text_prompt_manager


text_prompt_router = APIRouter(tags=["Text Prompts"])


@text_prompt_router.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(batch: TextPromptBatch, api_key: str = Depends(verify_api_key)) -> Response:  # noqa: B008
    text_prompt_manager.submit(batch=TextPromptBatch(prompts=batch.prompts))
    return Response()


@text_prompt_router.get("/get", response_model=TextPromptBatch)
async def get_strings(
    request: MetagraphData,
    metagraph: MetagraphManager = Depends(get_metagraph_manager),  # noqa: B008
) -> BasePromptBatch:
    if not metagraph.verify_signature(request.hotkey, request.nonce, request.signature):
        raise HTTPException(status_code=403, detail="Invalid signature provided.")
    batch = text_prompt_manager.get()
    return batch
