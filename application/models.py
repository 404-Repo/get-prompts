from pydantic import BaseModel, HttpUrl


class MetagraphDataDTO(BaseModel):
    """DTO object containing credentials for verifying validator's identity in bittensor network."""

    hotkey: str
    nonce: int
    signature: str


class ImagePromptFull(BaseModel):
    """Contains normalized text prompt and image prompt url."""

    url: HttpUrl
    normalized_prompt: str


class ImagePromptPartial(BaseModel):
    """Normalized prompt is optional comparing to the ImagePromptFull."""

    url: HttpUrl
    normalized_prompt: str | None = None


class ImagePromptSubmitDTO(BaseModel):
    prompts: list[ImagePromptFull]


class ImagePromptObtainDTO(BaseModel):
    prompts: list[ImagePromptPartial]


class TextPromptDTO(BaseModel):
    normalized_prompts: list[str]
