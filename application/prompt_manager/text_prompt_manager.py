from pathlib import Path

from application.config import config
from application.prompt_manager.base_prompt_manager import BasePromptManager
from application.utils.prompt_storage import InMemoryTextPromptStorage


class TextPromptManager(BasePromptManager[str]):
    _DEFAULT_PROMPTS_normalized_prompt: str = "default_prompts.txt"

    def __init__(
        self,
        *,
        submitted_text_storage: InMemoryTextPromptStorage,
        batch_size: int,
    ) -> None:
        super().__init__(batch_size=batch_size)
        self._prompt_storage = submitted_text_storage
        self._batch_size = batch_size

    def submit(self, *, batch: list[str]) -> None:  # type: ignore
        self._prompt_storage.add(prompts=batch)

    def get_batch(self) -> list[str]:  # type: ignore
        return self._prompt_storage.get_batch(batch_size=self._batch_size)


text_prompt_manager = TextPromptManager(
    submitted_text_storage=InMemoryTextPromptStorage(
        max_prompt_cnt=config.text_prompt_storage_size,
        default_prompt_path=Path(config.default_text_prompt_file),
    ),
    batch_size=config.text_prompt_batch_size,
)
