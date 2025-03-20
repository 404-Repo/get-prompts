from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, cast

import uvicorn
from application.config import config
from application.validators import Metagraph
from fastapi import Depends, FastAPI
from prompt_manager.schemas.prompt_batch import BasePromptBatch, TextPromptBatch
from prompt_manager.text_prompt_manager import text_prompt_manager
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_200_OK


app = FastAPI()
app.state.config = None
app.state.prompts = None
app.state.metagraph = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    app.state.config = config
    app.state.metagraph = Metagraph(config)
    yield


def get_metagraph() -> Metagraph:
    return cast(Metagraph, app.state.metagraph)


@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(
    batch: TextPromptBatch,  # api_key: str = Depends(verify_api_key)  # noqa: B008
) -> Response:
    text_prompt_manager.submit(batch=TextPromptBatch(prompts=batch.prompts))
    return Response()


class RequestModel(BaseModel):
    hotkey: str
    nonce: int
    signature: str


@app.post("/get", response_model=TextPromptBatch)
async def get_strings(
    request: RequestModel,
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> BasePromptBatch:
    # if not metagraph.verify_signature(request.hotkey, request.nonce, request.signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature provided.")
    batch = text_prompt_manager.get()
    return batch


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)  # noqa: S104
