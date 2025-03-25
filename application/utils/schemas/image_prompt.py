from pydantic import BaseModel


class ImagePrompt(BaseModel):
    image_data: bytes
    normalized_prompt: str = ""
