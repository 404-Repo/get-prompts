from enum import Enum
from typing import Any
from urllib.parse import urlencode


class Routes(Enum):
    """The enum class is used for representing routes of our system for the tests."""

    NONE = ""

    SUBMIT_TEXT_PROMPTS = "/text_prompts/submit"
    BATCH_TEXT_PROMPTS = "/text_prompts/batch"

    SUBMIT_IMAGE_PROMPTS = "/image_prompts/submit"
    BATCH_IMAGE_PROMPTS = "/image_prompts/batch"

    LEGACY_TEXT_PROMPTS_BATCH = "/batch"
    LEGACY_TEXT_PROMPTS_SUBMIT = "/submit"


def construct_url(url: Routes, query_params: dict[str, Any] | None = None, **kwargs: Any) -> str:
    """
    The method constructs url from url, arguments, and query params.
    """

    result_url: str = url.value.format(**kwargs)
    if query_params is not None:
        query_string = urlencode(query_params)
        result_url = f"{result_url}?{query_string}"

    return result_url
