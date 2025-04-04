from typing import cast

from application.app import app
from application.config import config
from application.dependencies import get_metagraph, verify_api_key
from application.models import ImagePromptFull, ImagePromptObtainDTO, ImagePromptSubmitDTO, MetagraphDataDTO
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import HttpUrl
from tests.mocks import fake_get_metagraph, fake_verify_api_key
from tests.routes import Routes, construct_url


app.dependency_overrides[get_metagraph] = fake_get_metagraph
app.dependency_overrides[verify_api_key] = fake_verify_api_key

fake = Faker()


class TestImagePromptEndpoints:
    def test_submit_and_retrieve_success(
        self, test_client: TestClient, api_headers: dict[str, str], metagraph_data: MetagraphDataDTO
    ) -> None:
        promts: dict[str, str] = {fake.url(): fake.sentence() for _ in range(20)}
        req_prompts: list[ImagePromptFull] = []
        for url, prompt in promts.items():
            req_prompts.append(
                ImagePromptFull(
                    url=cast(HttpUrl, url),
                    normalized_prompt=prompt,
                )
            )
        request_data = ImagePromptSubmitDTO(prompts=req_prompts)
        json_data = request_data.model_dump()
        for prompt in json_data["prompts"]:
            prompt["url"] = str(prompt["url"])  # type: ignore
        response = test_client.post(construct_url(Routes.SUBMIT_IMAGE_PROMPTS), json=json_data, headers=api_headers)
        assert response.status_code == 200

        response = test_client.post(
            construct_url(Routes.BATCH_IMAGE_PROMPTS, {"include_normalized_prompt": "true"}),
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        batch_prompts = ImagePromptObtainDTO.model_validate(response.json()).prompts
        batch_prompts_dict = {str(prompt.url): prompt.normalized_prompt for prompt in batch_prompts}
        for url, prompt in promts.items():
            assert url in batch_prompts_dict
            assert prompt in cast(str, batch_prompts_dict[url])

    def test_get_default_image_prompts_batch_without_text_success(
        self,
        test_client: TestClient,
        metagraph_data: MetagraphDataDTO,
    ) -> None:
        response = test_client.post(construct_url(Routes.BATCH_IMAGE_PROMPTS), json=metagraph_data.model_dump())
        assert response.status_code == 200
        batch_prompts = ImagePromptObtainDTO.model_validate(response.json()).prompts
        assert len(batch_prompts) == config.image_prompt_batch_size
        for prompt in batch_prompts:
            assert prompt.normalized_prompt is None

    def test_get_default_image_prompts_batch_with_text_success(
        self,
        test_client: TestClient,
        metagraph_data: MetagraphDataDTO,
    ) -> None:
        response = test_client.post(
            construct_url(Routes.BATCH_IMAGE_PROMPTS, {"include_normalized_prompt": "true"}),
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        batch_prompts = ImagePromptObtainDTO.model_validate(response.json()).prompts
        assert len(batch_prompts) == config.image_prompt_batch_size
        for prompt in batch_prompts:
            assert prompt.normalized_prompt is not None
