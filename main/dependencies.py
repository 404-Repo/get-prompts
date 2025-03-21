from bittensor import Metagraph
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from main.config import config


metagraph = Metagraph(network=config.network, netuid=config.netuid)
api_key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)


def get_metagraph() -> Metagraph:
    global metagraph
    if metagraph is None:
        metagraph = Metagraph(config)
    return metagraph


def verify_api_key(x_api_key: str = Security(api_key_header)) -> str:
    if x_api_key != config.api_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key
