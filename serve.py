from application.prompts import Prompts
from application.settings import settings
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_403_FORBIDDEN


app = FastAPI()
prompts = Prompts()

api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)


class Batch(BaseModel):
    prompts: list[str]


def verify_api_key(x_api_key: str = Security(api_key_header)) -> str:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key


@app.post("/submit", status_code=HTTP_200_OK, response_class=Response)
async def submit_strings(batch: Batch, api_key: str = Depends(verify_api_key)) -> Response:
    prompts.submit(batch.prompts)
    return Response()


@app.get("/get", response_model=Batch)
async def get_strings(hotkey: str, prompts_after: int, signature: str) -> Batch:
    return Batch(prompts=prompts.get())
