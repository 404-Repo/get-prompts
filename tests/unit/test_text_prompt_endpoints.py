from application.config import config
from application.models import MetagraphDataDTO, TextPromptDTO
from faker import Faker
from fastapi.testclient import TestClient
from tests.routes import Routes, construct_url


fake = Faker()


class TestTextPromptEndpoints:
    def test_submit_and_retrieve_strings_success(
        self,
        test_client: TestClient,
        api_headers: dict[str, str],
        metagraph_data: MetagraphDataDTO,
        setup_dependencies: None,
    ) -> None:
        promts = [fake.sentence() for _ in range(20)]
        request_data = TextPromptDTO(normalized_prompts=promts)
        response = test_client.post(
            construct_url(Routes.SUBMIT_TEXT_PROMPTS), json=request_data.model_dump(), headers=api_headers
        )
        assert response.status_code == 200
        response = test_client.post(
            construct_url(Routes.BATCH_TEXT_PROMPTS),
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        returned_prompts = TextPromptDTO.model_validate(response.json()).normalized_prompts
        for prompt in promts:
            assert prompt in returned_prompts

    def test_get_default_text_prompts_batch_success(
        self, test_client: TestClient, metagraph_data: MetagraphDataDTO, setup_dependencies: None
    ) -> None:
        response = test_client.post(construct_url(Routes.BATCH_TEXT_PROMPTS), json=metagraph_data.model_dump())
        assert response.status_code == 200
        response_data = TextPromptDTO.model_validate(response.json())
        assert len(response_data.normalized_prompts) == config.text_prompt_batch_size
