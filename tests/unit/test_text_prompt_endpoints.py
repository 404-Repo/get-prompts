from settings import settings
from api.models import GetPromptsRequest, GetPromptsResponse
from faker import Faker
from fastapi.testclient import TestClient
from routes import Routes, construct_url


fake = Faker()


class TestGetPromptsResponseEndpoints:
    def test_submit_and_retrieve_strings_success(
        self,
        test_client: TestClient,
        api_headers: dict[str, str],
        request_data: GetPromptsRequest,
        setup_dependencies: None,
    ) -> None:
        promts = [fake.sentence() for _ in range(20)]
        response_data = GetPromptsResponse(normalized_prompts=promts)
        response = test_client.post(
            construct_url(Routes.SUBMIT_TEXT_PROMPTS), json=response_data.model_dump(), headers=api_headers
        )
        assert response.status_code == 200
        response = test_client.post(
            construct_url(Routes.BATCH_TEXT_PROMPTS),
            json=request_data.model_dump(),
        )
        assert response.status_code == 200
        returned_prompts = GetPromptsResponse.model_validate(response.json()).normalized_prompts
        for prompt in promts:
            assert prompt in returned_prompts

    def test_get_default_text_prompts_batch_success(
        self, test_client: TestClient, request_data: GetPromptsRequest, setup_dependencies: None
    ) -> None:
        response = test_client.post(construct_url(Routes.BATCH_TEXT_PROMPTS), json=request_data.model_dump())
        assert response.status_code == 200
        response_data = GetPromptsResponse.model_validate(response.json())
        assert len(response_data.normalized_prompts) == settings.text_prompt_batch_size
