from fastapi import Security
from fastapi.security import APIKeyHeader
from utils.metagraph_manager import MetagraphManager

from main.config import config
from main.exceptions import InvalidApiKeyException


metagraph = MetagraphManager(config=config)
api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)


def get_metagraph_manager() -> MetagraphManager:
    return metagraph


def verify_api_key(x_api_key: str = Security(api_key_header)) -> str:
    if x_api_key != config.api_key:
        raise InvalidApiKeyException("Invalid API key provided.")
    return x_api_key
