from pydantic import BaseModel, HttpUrl
from prompt_storage.image_prompt import ImagePrompt


class MetagraphDataDTO(BaseModel):
    """DTO object containing credentials for verifying validator's identity in bittensor network."""

    hotkey: str
    nonce: int
    signature: str
    

class ImagePromptSubmitDTO(BaseModel):
    prompts: list[ImagePrompt]


class ImagePromptObtainDTO(BaseModel):
    prompts: list[ImagePrompt]


class TextPromptDTO(BaseModel):
    normalized_prompts: list[str]
