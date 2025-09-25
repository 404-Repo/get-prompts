from settings import settings
from api.models import MetagraphDataDTO
from faker import Faker
from fastapi.testclient import TestClient
from routes import Routes, construct_url


fake = Faker()


class TestLegacyTextPromptEndpoints:
    def test_submit_and_retrieve_strings_success(
        self,
        test_client: TestClient,
        api_headers: dict[str, str],
        metagraph_data: MetagraphDataDTO,
        setup_dependencies: None,
    ) -> None:
        promts = [fake.sentence() for _ in range(20)]
        response = test_client.post(construct_url(Routes.LEGACY_TEXT_PROMPTS_SUBMIT), json=promts, headers=api_headers)
        assert response.status_code == 200
        response = test_client.post(
            construct_url(Routes.LEGACY_TEXT_PROMPTS_BATCH),
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        returned_prompts = response.json()
        for prompt in promts:
            assert prompt in returned_prompts

    def test_get_default_text_prompts_batch_success(
        self, test_client: TestClient, metagraph_data: MetagraphDataDTO, setup_dependencies: None
    ) -> None:
        response = test_client.post(construct_url(Routes.LEGACY_TEXT_PROMPTS_BATCH), json=metagraph_data.model_dump())
        assert response.status_code == 200
        assert len(response.json()) == settings.text_prompt_batch_size
