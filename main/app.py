from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from config import config
from fastapi import FastAPI
from prompt_manager.image_prompt_endpoints import image_prompt_router
from prompt_manager.schemas.prompt_batch import BasePromptBatch, TextPromptBatch
from prompt_manager.text_prompt_manager import text_prompt_manager
from starlette.responses import Response
from starlette.status import HTTP_200_OK


app = FastAPI()
app.include_router(image_prompt_router, prefix="/images")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    yield


@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(
    batch: TextPromptBatch,  # api_key: str = Depends(verify_api_key)  # noqa: B008
) -> Response:
    text_prompt_manager.submit(batch=TextPromptBatch(prompts=batch.prompts))
    return Response()


@app.get("/get", response_model=TextPromptBatch)
async def get_strings(
    # request: MetagraphData,
    # metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> BasePromptBatch:
    # if not metagraph.verify_signature(request.hotkey, request.nonce, request.signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature provided.")
    batch = text_prompt_manager.get()
    return batch


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)  # noqa: S104
