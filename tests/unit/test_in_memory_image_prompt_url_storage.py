from pathlib import Path

import faker
import pytest
from application.config import config
from application.exceptions import FileWithTextDataDoesntExist, NotEnoughPromptsAvailable
from application.prompt.prompt_storage import InMemoryImagePromptStorage


fake = faker.Faker()


class TestInMemoryImagePromptUrlStorage:
    _MAX_URL_CNT: int = 1000

    def test_image_prompt_url_storage_initialized_with_default(self) -> None:
        storage = self._get_storage()
        assert storage.url_cnt == 0
        assert len(storage._url_to_normalized_prompt) > 0

    def test_image_prompt_url_storage_raises_error_if_no_default_prompts(self) -> None:
        with pytest.raises(FileWithTextDataDoesntExist):
            self._get_storage(Path("temp/doesnt_exist.csv"))

    def test_max_url_count_not_exceeded(self) -> None:
        storage = self._get_storage()
        new_prompts = {
            f"https://example.com/image_{i}.webp": f"prompt_{i}"
            for i in range(TestInMemoryImagePromptUrlStorage._MAX_URL_CNT)
        }
        storage.add(prompts=new_prompts)
        assert storage.url_cnt == TestInMemoryImagePromptUrlStorage._MAX_URL_CNT

    def test_submitted_prompts_are_returned_first(self) -> None:
        batch_size = 10
        storage = self._get_storage()
        new_prompts = {f"https://example.com/image_{i}.webp": f"prompt_{i}" for i in range(batch_size)}
        storage.add(prompts=new_prompts)
        batch_prompts = storage.get_batch(batch_size=batch_size)
        for url, prompt in new_prompts.items():
            assert url in batch_prompts
            assert prompt in batch_prompts[url]
            assert batch_prompts[url] == prompt

    def test_get_batch_raises_error_if_not_enough_prompts(self) -> None:
        storage = self._get_storage()
        total_available = storage.url_cnt + len(storage._url_to_normalized_prompt)
        with pytest.raises(NotEnoughPromptsAvailable):
            storage.get_batch(batch_size=total_available + 1)

    def test_get_batch_returns_default_prompts_if_no_new_prompts(self) -> None:
        storage = self._get_storage()
        batch_size = 5
        batch = storage.get_batch(batch_size=batch_size)
        assert len(batch) == batch_size
        for url, prompt in batch.items():
            assert url in storage._url_to_normalized_prompt
            assert prompt in storage._url_to_normalized_prompt[url]

    def _get_storage(
        self, default_image_url_file: Path = Path(config.default_image_url_file)
    ) -> InMemoryImagePromptStorage:
        return InMemoryImagePromptStorage(
            max_url_cnt=TestInMemoryImagePromptUrlStorage._MAX_URL_CNT,
            default_image_url_file_path=default_image_url_file,
        )
