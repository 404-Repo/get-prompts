import pytest
from application.app import app
from application.config import config
from application.dependencies import get_metagraph, verify_api_key
from application.metagraph import Metagraph
from application.models import MetagraphDataDTO
from fastapi.testclient import TestClient


@pytest.fixture
def test_client() -> TestClient:
    """Fixture to create a test client."""
    return TestClient(app)


@pytest.fixture
def api_headers() -> dict[str, str]:
    """Fixture to provide test API headers."""
    return {"X-Api-Key": "test_api_key"}


@pytest.fixture
def metagraph_data() -> MetagraphDataDTO:
    """Fixture to provide test metagraph data."""
    return MetagraphDataDTO(hotkey="test_hotkey", nonce=12345, signature="test_signature")


class MockMetagraph(Metagraph):
    def verify_signature(self, hotkey: str, nonce: int, signature: str) -> None:
        pass

    async def sync(self) -> None:
        pass


def fake_get_metagraph() -> MockMetagraph:
    return MockMetagraph(config=config)


def fake_verify_api_key() -> str:
    return "test_api_key"


@pytest.fixture
def setup_dependencies() -> None:
    app.dependency_overrides[get_metagraph] = fake_get_metagraph
    app.dependency_overrides[verify_api_key] = fake_verify_api_key
