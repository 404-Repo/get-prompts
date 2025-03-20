from pathlib import Path

from pydantic import BaseModel


class BasePromptBatch(BaseModel):
    pass


class TextPromptBatch(BasePromptBatch):
    prompts: list[str]


class ImagePromptBatch(BasePromptBatch):
    archive_path: Path
