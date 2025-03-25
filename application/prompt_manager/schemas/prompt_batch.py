from pydantic import BaseModel

from application.utils.schemas.image_prompt import ImagePrompt


class BasePromptBatch(BaseModel):
    pass


class TextPromptBatch(BasePromptBatch):
    prompts: list[str]


class ImagePromptBatch(BasePromptBatch):
    image_prompts: list[ImagePrompt]


# todo remove
