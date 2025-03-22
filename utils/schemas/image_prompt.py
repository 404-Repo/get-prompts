from io import BytesIO

from pydantic import BaseModel


class ImagePrompt(BaseModel):
    image_data: BytesIO
    filename: str
