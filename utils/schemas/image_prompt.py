from dataclasses import dataclass


@dataclass
class ImagePrompt:
    image_data: bytes
    filename: str
