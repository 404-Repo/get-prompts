from pydantic import BaseModel, HttpUrl
from prompt_storage import PromptStorage


class GetPromptsRequest(BaseModel):
    hotkey: str
    nonce: int
    signature: str


class SubmitPromptsRequest(BaseModel):
    prompts: list[str]


class GetPromptsResponse(BaseModel):
    prompts: list[str]
