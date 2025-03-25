from fastapi import Security
from fastapi.security import APIKeyHeader

from application.config import config
from application.exceptions import InvalidApiKeyException
from application.utils.metagraph_manager import MetagraphManager


metagraph_manager = MetagraphManager(config=config)
api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)


def get_metagraph_manager() -> MetagraphManager:
    return metagraph_manager


def verify_api_key(x_api_key: str = Security(api_key_header)) -> str:
    if x_api_key != config.api_key:
        raise InvalidApiKeyException("Invalid API key provided.")
    return x_api_key
