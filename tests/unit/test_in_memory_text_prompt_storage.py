from pathlib import Path

import faker
import pytest
from main.exceptions import FileWithTextDataDoesntExist
from utils.prompt_storage import InMemoryTextPromptStorage


fake = faker.Faker()


class TestInMemoryTextPromptStorage:
    _MAX_PROMPT_CNT: int = 100000

    def test_text_promp_storage_initialized_with_default(self) -> None:
        storage = self._get_storage()
        assert storage.prompts_cnt >= TestInMemoryTextPromptStorage._MAX_PROMPT_CNT

    def test_text_promp_storage_raises_error_if_no_default_prompts(self) -> None:
        with pytest.raises(FileWithTextDataDoesntExist):
            self._get_storage(Path("temp/doesnt_exist.txt"))

    def test_max_prompt_count_not_exceeded(self) -> None:
        storage = self._get_storage()
        new_prompts = [fake.sentence() for _ in range(TestInMemoryTextPromptStorage._MAX_PROMPT_CNT)]
        storage.add(prompts=new_prompts)
        assert storage.prompts_cnt == TestInMemoryTextPromptStorage._MAX_PROMPT_CNT

    def test_submitted_prompts_remove_default(self) -> None:
        storage = self._get_storage()
        new_prompts = [f"temp_{idx}" for idx in range(TestInMemoryTextPromptStorage._MAX_PROMPT_CNT)]
        storage.add(prompts=new_prompts)
        prompts = storage.get_batch(batch_size=TestInMemoryTextPromptStorage._MAX_PROMPT_CNT)
        for prompt in prompts:
            assert prompt.startswith("temp_")

    def _get_storage(
        self, default_prompts_file: Path = Path("resources/texts/default_prompts.txt")
    ) -> InMemoryTextPromptStorage:
        return InMemoryTextPromptStorage(
            max_text_cnt=TestInMemoryTextPromptStorage._MAX_PROMPT_CNT,
            file_path=default_prompts_file,
        )
