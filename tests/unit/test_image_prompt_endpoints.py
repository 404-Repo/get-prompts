from typing import cast

from settings import settings
from api.models import ImagePrompt, GetPromptsResponse, ImagePromptSubmit, MetagraphData
from faker import Faker
from fastapi.testclient import TestClient
from pydantic import HttpUrl
from routes import Routes, construct_url


fake = Faker()


class TestImagePromptEndpoints:
    def test_submit_and_retrieve_success(
        self,
        test_client: TestClient,
        api_headers: dict[str, str],
        metagraph_data: MetagraphData,
        setup_dependencies: None,
    ) -> None:
        promts: dict[str, str] = {fake.url(): fake.sentence() for _ in range(20)}

        # Submit image prompts
        req_prompts: list[ImagePrompt] = []
        for url, prompt in promts.items():
            req_prompts.append(
                ImagePrompt(
                    url=cast(HttpUrl, url),
                    normalized_prompt=prompt,
                )
            )
        request_data = ImagePromptSubmit(prompts=req_prompts)
        json_data = request_data.model_dump()
        for prompt in json_data["prompts"]:
            prompt["url"] = str(prompt["url"])  # type: ignore
        response = test_client.post(construct_url(Routes.SUBMIT_IMAGE_PROMPTS), json=json_data, headers=api_headers)
        assert response.status_code == 200

        # Retrieve image prompts
        response = test_client.post(
            construct_url(Routes.BATCH_IMAGE_PROMPTS, {"include_normalized_prompt": "true"}),
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        batch_prompts = GetPromptsResponse.model_validate(response.json()).prompts
        batch_prompts_dict = {str(prompt.url): prompt.normalized_prompt for prompt in batch_prompts}
        for url, prompt in promts.items():
            assert url in batch_prompts_dict
            assert prompt in cast(str, batch_prompts_dict[url])

    def test_get_default_image_prompts_batch_without_text_success(
        self, test_client: TestClient, metagraph_data: MetagraphData, setup_dependencies: None
    ) -> None:
        response = test_client.post(construct_url(Routes.BATCH_IMAGE_PROMPTS), json=metagraph_data.model_dump())
        assert response.status_code == 200
        batch_prompts = GetPromptsResponse.model_validate(response.json()).prompts
        assert len(batch_prompts) == settings.image_prompt_batch_size
        for prompt in batch_prompts:
            assert prompt.normalized_prompt is None

    def test_get_default_image_prompts_batch_with_text_success(
        self, test_client: TestClient, metagraph_data: MetagraphData, setup_dependencies: None
    ) -> None:
        response = test_client.post(
            construct_url(Routes.BATCH_IMAGE_PROMPTS, {"include_normalized_prompt": "true"}),
            json=metagraph_data.model_dump(),
        )
        assert response.status_code == 200
        batch_prompts = GetPromptsResponse.model_validate(response.json()).prompts
        assert len(batch_prompts) == settings.image_prompt_batch_size
        for prompt in batch_prompts:
            assert prompt.normalized_prompt is not None
