from application.prompt.base_prompt import BasePrompt
from application.prompt.prompt_storage import InMemoryImagePromptUrlStorage, image_prompt_url_storage


class ImagePrompt(BasePrompt):
    def __init__(
        self,
        *,
        image_prompt_url_storage: InMemoryImagePromptUrlStorage,
    ) -> None:
        self._image_prompt_url_storage = image_prompt_url_storage

    def submit(self, *, batch: dict[str, str]) -> None:  # type: ignore
        self._image_prompt_url_storage.add(prompts=batch)

    def get_batch(self, *, batch_size: int) -> dict[str, str]:
        # todo Check that file is actually image in webp format
        return self._image_prompt_url_storage.get_batch(batch_size=batch_size)


image_prompt = ImagePrompt(
    image_prompt_url_storage=image_prompt_url_storage,
)
