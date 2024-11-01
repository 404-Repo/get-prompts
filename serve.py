import typing

import uvicorn
from application.config import config
from application.prompts import Prompts
from application.utils import verify_api_key
from application.validators import Metagraph
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_200_OK


app = FastAPI()
app.state.config = None
app.state.prompts = None
app.state.metagraph = None


@app.on_event("startup")
def startup_event() -> None:
    app.state.config = config
    app.state.prompts = Prompts(config)
    app.state.metagraph = Metagraph(config)


def get_prompts_manager() -> Prompts:
    return typing.cast(Prompts, app.state.prompts)


def get_metagraph() -> Metagraph:
    return typing.cast(Metagraph, app.state.metagraph)


class Batch(BaseModel):
    prompts: list[str]


@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(
    batch: Batch, 
    request: Request,
    prompts: Prompts = Depends(get_prompts_manager), 
    api_key: str = Depends(verify_api_key)  # noqa: B008
) -> Response:
    client_ip = request.headers.get("X-POD-ID")
    prompts.submit(batch.prompts, client_ip)
    return Response()


class RequestModel(BaseModel):
    hotkey: str
    nonce: int
    signature: str


@app.get("/get", response_model=Batch)
async def get_strings(
    request: RequestModel,
    prompts: Prompts = Depends(get_prompts_manager),  # noqa: B008
    metagraph: Metagraph = Depends(get_metagraph),  # noqa: B008
) -> Batch:
    if not metagraph.verify_signature(request.hotkey, request.nonce, request.signature):
        raise HTTPException(status_code=403, detail="Invalid signature provided.")
    return Batch(prompts=prompts.get())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)  # noqa: S104
