from application.prompt.base_prompt import BasePrompt
from application.prompt.prompt_storage import InMemoryImagePromptStorage, image_prompt_storage


class ImagePrompt(BasePrompt):
    def __init__(
        self,
        *,
        image_prompt_storage: InMemoryImagePromptStorage,
    ) -> None:
        self._image_prompt_storage = image_prompt_storage

    def submit(self, *, batch: dict[str, str]) -> None:
        self._image_prompt_storage.add(prompts=batch)

    def get_batch(self, *, batch_size: int) -> dict[str, str]:
        return self._image_prompt_storage.get_batch(batch_size=batch_size)


image_prompt = ImagePrompt(
    image_prompt_storage=image_prompt_storage,
)
