from pydantic import BaseModel
from utils.schemas.image_prompt import ImagePrompt


class BasePromptBatch(BaseModel):
    pass


class TextPromptBatch(BasePromptBatch):
    prompts: list[str]


class ImagePromptBatch(BasePromptBatch):
    image_prompts: list[ImagePrompt]
