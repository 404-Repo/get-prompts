from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.status import HTTP_200_OK

from application.dependencies import get_metagraph_manager, verify_api_key
from application.prompt_manager.text_prompt import text_prompt_manager
from application.utils.metagraph import Metagraph
from application.utils.schemas.metagraph_data import MetagraphData


text_prompt_router = APIRouter(tags=["Text Prompts"])


@text_prompt_router.post(
    path="/submit", status_code=HTTP_200_OK, summary="Submit text prompts", response_class=Response
)
async def submit_strings(batch: list[str], api_key: str = Depends(verify_api_key)) -> Response:  # noqa: B008
    text_prompt_manager.submit(batch=batch)
    return Response()


@text_prompt_router.post(path="/download", summary="Fetch a batch of text prompts")
async def fetch_text_prompt_batch(
    request: MetagraphData,
    metagraph: Metagraph = Depends(get_metagraph_manager),  # noqa: B008
) -> list[str]:
    metagraph.verify_signature(request.hotkey, request.nonce, request.signature)
    batch = text_prompt_manager.get_batch()
    return batch
