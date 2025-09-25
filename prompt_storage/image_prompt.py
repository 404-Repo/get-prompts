from pydantic import BaseModel, HttpUrl


class ImagePrompt(BaseModel):
    normalize_text_prompt: str | None = None
    """Normalized text prompt from which the image was generated."""
    url: HttpUrl
    """URL of the image in the S3-compatible storage."""

    def __hash__(self) -> int:
        return hash((self.url, self.normalize_text_prompt))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImagePrompt):
            return False
        return self.url == other.url and self.normalize_text_prompt == other.normalize_text_prompt
    