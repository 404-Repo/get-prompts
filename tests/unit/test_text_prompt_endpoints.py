from application.app import app
from application.config import config
from application.dependencies import get_metagraph, verify_api_key
from application.models import MetagraphDataDTO, TextPromptDTO
from fastapi.testclient import TestClient
from tests.unit.mocks import fake_get_metagraph, fake_verify_api_key


app.dependency_overrides[get_metagraph] = fake_get_metagraph
app.dependency_overrides[verify_api_key] = fake_verify_api_key


class TestTextPromptEndpoints:
    def test_submit_and_retrieve_strings_success(
        self, test_client: TestClient, api_headers: dict[str, str], metagraph_data: MetagraphDataDTO
    ) -> None:
        promts = ["prompt1", "prompt2"]
        request_data = TextPromptDTO(normalized_prompts=promts)
        response = test_client.post("/text_prompts/submit", json=request_data.model_dump(), headers=api_headers)
        assert response.status_code == 200
        response = test_client.post(
            "/text_prompts/batch",
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        returned_prompts = response.json()
        for prompt in promts:
            assert prompt in returned_prompts

    def test_get_default_text_prompts_batch_success(
        self,
        test_client: TestClient,
        metagraph_data: MetagraphDataDTO,
    ) -> None:
        response = test_client.post("/text_prompts/batch", json=metagraph_data.model_dump())
        assert response.status_code == 200
        assert len(response.json()) == config.text_prompt_batch_size
