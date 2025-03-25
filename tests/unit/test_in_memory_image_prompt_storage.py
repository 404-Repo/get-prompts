import random
from pathlib import Path

import faker
import pytest
from application.exceptions import NoDefaultImagePrompts
from application.utils.prompt_storage import InMemoryImagePromptStorage
from application.utils.schemas.image_prompt import ImagePrompt


fake = faker.Faker()


class TestInMemoryImagePromptStorage:
    _MAX_PROMPT_CNT: int = 100

    def test_image_promp_storage_initialized_with_default(self) -> None:
        storage = self._get_storage()
        assert storage.prompt_cnt >= TestInMemoryImagePromptStorage._MAX_PROMPT_CNT

    def test_image_promp_storage_raises_error_if_no_default_prompts(self) -> None:
        with pytest.raises(NoDefaultImagePrompts):
            self._get_storage(Path("temp/doesnt_exist"))

    def test_max_prompt_count_not_exceeded(self) -> None:
        storage = self._get_storage()
        for _ in range(10):
            new_prompts = [
                ImagePrompt(
                    normalized_prompt=fake.sentence(),
                    image_data=bytes.fromhex(TestInMemoryImagePromptStorage._random_hex_string(32)),
                )
                for _ in range(
                    random.randint(  # noqa: S311
                        TestInMemoryImagePromptStorage._MAX_PROMPT_CNT // 2,
                        TestInMemoryImagePromptStorage._MAX_PROMPT_CNT,
                    )
                )
            ]
            storage.add(prompts=new_prompts)
            max_count_achieved = storage.prompt_cnt >= TestInMemoryImagePromptStorage._MAX_PROMPT_CNT
            if not max_count_achieved:
                assert storage.prompt_cnt < TestInMemoryImagePromptStorage._MAX_PROMPT_CNT
            else:
                assert storage.prompt_cnt == TestInMemoryImagePromptStorage._MAX_PROMPT_CNT

    def test_submitted_prompts_remove_default(self) -> None:
        storage = self._get_storage(default_prompts_dir=Path("resources/images/default"))

        new_prompts = [
            ImagePrompt(
                normalized_prompt=f"temp_{idx}.webp",
                image_data=bytes.fromhex(TestInMemoryImagePromptStorage._random_hex_string(32)),
            )
            for idx in range(TestInMemoryImagePromptStorage._MAX_PROMPT_CNT)
        ]
        storage.add(prompts=new_prompts)
        prompts = storage.get_batch(batch_size=TestInMemoryImagePromptStorage._MAX_PROMPT_CNT)
        for prompt in prompts:
            assert prompt.normalized_prompt.startswith("temp_")

    def _get_storage(self, default_prompts_dir: Path = Path("resources/images/default")) -> InMemoryImagePromptStorage:
        return InMemoryImagePromptStorage(
            max_prompt_cnt=TestInMemoryImagePromptStorage._MAX_PROMPT_CNT,
            default_resources_dir=default_prompts_dir,
        )

    @staticmethod
    def _random_hex_string(length: int = 16) -> str:
        return "".join(random.choices("0123456789abcdef", k=length))  # noqa: S311
