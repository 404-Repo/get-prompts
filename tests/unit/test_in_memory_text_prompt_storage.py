from pathlib import Path

import faker
import pytest
from application.config import config
from application.exceptions import FileWithTextDataDoesntExist, NotEnoughPromptsAvailable
from application.prompt.prompt_storage import InMemoryTextPromptStorage


fake = faker.Faker()


class TestInMemoryTextPromptStorage:
    _MAX_PROMPT_CNT: int = 1000

    def test_text_promp_storage_initialized_with_default(self) -> None:
        storage = self._get_storage()
        default_file_path = Path(config.default_text_prompt_file)
        assert storage.prompt_cnt == 0
        with default_file_path.open(mode="r") as f:
            lines_cnt = len(set(f.readlines()))
            assert storage.all_prompt_cnt == lines_cnt

    def test_text_promp_storage_raises_error_if_no_default_prompts(self) -> None:
        with pytest.raises(FileWithTextDataDoesntExist):
            self._get_storage(Path("temp/doesnt_exist.txt"))

    def test_max_prompt_count_not_exceeded(self) -> None:
        storage = self._get_storage()
        new_prompts = [fake.sentence() for _ in range(TestInMemoryTextPromptStorage._MAX_PROMPT_CNT)]
        storage.add(prompts=new_prompts)
        assert storage.prompt_cnt == TestInMemoryTextPromptStorage._MAX_PROMPT_CNT

    def test_submitted_prompts_are_returned_first(self) -> None:
        batch_size = 10
        storage = self._get_storage()
        new_prompts = [f"temp_{idx}" for idx in range(batch_size)]
        storage.add(prompts=new_prompts)
        batch_prompts = storage.get_batch(batch_size=batch_size)
        for prompt in new_prompts:
            assert any(prompt == batch_prompt for batch_prompt in batch_prompts)

    def test_get_batch_raises_error_if_not_enough_prompts(self) -> None:
        storage = self._get_storage()
        total_available = storage.prompt_cnt + len(storage._all_prompts)
        with pytest.raises(NotEnoughPromptsAvailable):
            storage.get_batch(batch_size=total_available + 1)

    def test_get_batch_returns_default_prompts_if_no_new_prompts(self) -> None:
        storage = self._get_storage()
        batch_size = 5
        batch = storage.get_batch(batch_size=batch_size)
        assert len(batch) == batch_size
        for prompt in batch:
            assert prompt in storage._all_prompts

    def _get_storage(
        self, default_prompts_file: Path = Path(config.default_text_prompt_file)
    ) -> InMemoryTextPromptStorage:
        return InMemoryTextPromptStorage(
            max_prompt_cnt=TestInMemoryTextPromptStorage._MAX_PROMPT_CNT,
            default_prompt_file_path=default_prompts_file,
        )
