from pathlib import Path

import faker
import pytest
from application.config import config
from application.exceptions import FileWithTextDataDoesntExist
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

    def test_submitted_prompts_remove_default(self) -> None:
        storage = self._get_storage()
        new_prompts = [f"temp_{idx}" for idx in range(TestInMemoryTextPromptStorage._MAX_PROMPT_CNT)]
        storage.add(prompts=new_prompts)
        prompts = storage.get_batch(batch_size=TestInMemoryTextPromptStorage._MAX_PROMPT_CNT)
        for prompt in prompts:
            assert prompt.startswith("temp_")

    def test_submitted_prompts_are_returned_first(self) -> None:
        batch_size = 10
        storage = self._get_storage()
        new_prompts = [f"temp_{idx}" for idx in range(batch_size)]
        storage.add(prompts=new_prompts)
        batch_prompts = storage.get_batch(batch_size=batch_size)
        for prompt in new_prompts:
            assert any(prompt == batch_prompt for batch_prompt in batch_prompts)

    def _get_storage(
        self, default_prompts_file: Path = Path("resources/text_prompts/default_prompts.txt")
    ) -> InMemoryTextPromptStorage:
        return InMemoryTextPromptStorage(
            max_prompt_cnt=TestInMemoryTextPromptStorage._MAX_PROMPT_CNT,
            default_prompt_file_path=default_prompts_file,
        )
