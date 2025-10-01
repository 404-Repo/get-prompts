from functools import cached_property
from pathlib import Path

from fastapi import Security
from fastapi.security import APIKeyHeader

from settings import settings
from exceptions import InvalidApiKeyException
from metagraph.metagraph import Metagraph
from metagraph.config import read_config
from prompt_storage import PromptStorage


config = read_config()
metagraph = Metagraph(config=config)
api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)


def get_metagraph() -> Metagraph:
    return metagraph


def verify_api_key(x_api_key: str = Security(api_key_header)) -> str:
    if x_api_key != settings.api_key:
        raise InvalidApiKeyException("Invalid API key provided.")
    return x_api_key


class StorageManager:
    @cached_property
    def text_prompt_storage(self) -> PromptStorage:
        return PromptStorage(
            storage_size=settings.text_prompt_storage_size,
            batch_size=settings.text_prompt_batch_size,
            default_prompt_file_path=Path(settings.text_prompt_default_file)
        )
    
    @cached_property
    def image_prompt_storage(self) -> PromptStorage:
        return PromptStorage(
            storage_size=settings.image_prompt_storage_size,
            batch_size=settings.image_prompt_batch_size,
            default_prompt_file_path=Path(settings.image_prompt_default_file)
        )


_storage_manager = StorageManager()


def get_text_prompt_storage() -> PromptStorage:
    return _storage_manager.text_prompt_storage


def get_image_prompt_storage() -> PromptStorage:
    return _storage_manager.image_prompt_storage
    