from application.prompt_manager.base_prompt import BasePrompt
from application.prompt_manager.prompt_storage import InMemoryTextPromptStorage, text_prompt_storage


class TextPrompt(BasePrompt):
    def __init__(
        self,
        *,
        text_prompt_storage: InMemoryTextPromptStorage,
    ) -> None:
        self._text_prompt_storage = text_prompt_storage

    def submit(self, *, batch: list[str]) -> None:  # type: ignore
        self._text_prompt_storage.add(prompts=batch)

    def get_batch(self, *, batch_size: int) -> list[str]:  # type: ignore
        return self._text_prompt_storage.get_batch(batch_size=batch_size)


text_prompt = TextPrompt(text_prompt_storage=text_prompt_storage)
