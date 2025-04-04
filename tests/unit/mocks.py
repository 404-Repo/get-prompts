from application.config import config
from application.metagraph import Metagraph


class MockMetagraph(Metagraph):
    def verify_signature(self, hotkey: str, nonce: int, signature: str) -> None:
        pass

    async def sync(self) -> None:
        pass


def fake_get_metagraph() -> MockMetagraph:
    return MockMetagraph(config=config)


def fake_verify_api_key() -> str:
    return "test_api_key"
