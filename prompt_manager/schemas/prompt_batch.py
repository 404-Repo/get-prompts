from pydantic import BaseModel
from utils.schemas.image_data import ImageData


class BasePromptBatch(BaseModel):
    pass


class TextPromptBatch(BasePromptBatch):
    prompts: list[str]


class ImagePromptBatch(BasePromptBatch):
    image_datas: list[ImageData]
