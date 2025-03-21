from io import BytesIO

from pydantic import BaseModel


class ImageData(BaseModel):
    data: BytesIO
    filename: str
