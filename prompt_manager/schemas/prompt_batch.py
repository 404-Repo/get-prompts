from pydantic import BaseModel


class BasePromptBatch(BaseModel):
    pass


class TextPromptBatch(BasePromptBatch):
    prompts: list[str]
