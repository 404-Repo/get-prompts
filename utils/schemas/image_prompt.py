from pydantic import BaseModel


class ImagePrompt(BaseModel):
    image_data: bytes
    filename: str
