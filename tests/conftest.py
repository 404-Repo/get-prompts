import pytest
from application.app import app
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
