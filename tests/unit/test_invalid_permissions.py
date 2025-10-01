import pytest
from application.app import app
from application.dependencies import get_metagraph, verify_api_key
from application.models import MetagraphData, GetPromptsResponse
from faker import Faker
from fastapi.testclient import TestClient
from tests.routes import Routes, construct_url


fake = Faker()


@pytest.fixture
def setup_data() -> None:
    # Change dependencies to the real ones.
    # They can be changed in other tests.
    app.dependency_overrides[get_metagraph] = get_metagraph
    app.dependency_overrides[verify_api_key] = verify_api_key


class TestInvalidPermissions:

    def test_invalid_api_key_failed(
        self, test_client: TestClient, api_headers: dict[str, str], setup_data: None
    ) -> None:
        promts = [fake.sentence() for _ in range(20)]
        request_data = GetPromptsResponse(normalized_prompts=promts)
        response = test_client.post(
            construct_url(Routes.SUBMIT_TEXT_PROMPTS), json=request_data.model_dump(), headers=api_headers
        )
        assert response.status_code == 403

    def test_invalid_signature_failed(
        self, test_client: TestClient, metagraph_data: MetagraphData, setup_data: None
    ) -> None:
        response = test_client.post(construct_url(Routes.BATCH_TEXT_PROMPTS), json=metagraph_data.model_dump())
        assert response.status_code == 403
