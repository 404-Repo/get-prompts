from pathlib import Path

from main.config import config
from utils.prompt_storage import InMemoryTextPromptStorage

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import TextPromptBatch


class TextPromptManager(BasePromptManager[TextPromptBatch]):
    _DEFAULT_PROMPTS_FILENAME: str = "default_prompts.txt"

    def __init__(
        self,
        *,
        default_text_storage: InMemoryTextPromptStorage,
        submitted_text_storage: InMemoryTextPromptStorage,
        batch_size: int,
    ) -> None:
        super().__init__(batch_size=batch_size)
        self._default_text_storage = default_text_storage
        self._submitted_text_storage = submitted_text_storage

    def submit(self, *, batch: TextPromptBatch) -> None:  # type: ignore
        self._submitted_text_storage.add(prompts=batch.prompts)

    def get_batch(self) -> TextPromptBatch:  # type: ignore
        texts = self._submitted_text_storage.get_batch(batch_size=self._batch_size)
        if len(texts) < self._batch_size:
            additional_text_cnt = self._batch_size - len(texts)
            default_texts = self._default_text_storage.get_batch(batch_size=additional_text_cnt)
            texts.extend(default_texts)
        return TextPromptBatch(prompts=texts)


text_prompt_manager = TextPromptManager(
    default_text_storage=InMemoryTextPromptStorage(
        max_text_cnt=config.text_prompt_storage_size,
        file_path=Path(config.default_text_prompt_file),
    ),
    submitted_text_storage=InMemoryTextPromptStorage(
        max_text_cnt=config.text_prompt_storage_size,
    ),
    batch_size=config.text_prompt_batch_size,
)
