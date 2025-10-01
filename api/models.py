from pydantic import BaseModel, HttpUrl
from prompt_storage import PromptStorage


class MetagraphData(BaseModel):
    """Model containing credentials for verifying validator's identity in bittensor network."""

    hotkey: str
    nonce: int
    signature: str


class SubmitPromptsRequest(BaseModel):
    prompts: list[str]


class GetPromptsResponse(BaseModel):
    prompts: list[str]
