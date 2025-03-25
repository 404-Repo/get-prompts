from pathlib import Path

from application.config import config
from application.prompt_manager.base_prompt_manager import BasePromptManager
from application.utils.prompt_storage import InMemoryImagePromptStorage
from application.utils.schemas.image_prompt import ImagePrompt


class ImagePromptManager(BasePromptManager[ImagePrompt]):
    def __init__(
        self,
        *,
        batch_size: int,
        prompt_storage: InMemoryImagePromptStorage,
    ) -> None:
        super().__init__(batch_size=batch_size)
        self._prompt_storage = prompt_storage

    def submit(self, *, batch: list[ImagePrompt]) -> None:  # type: ignore
        self._prompt_storage.add(prompts=batch)

    async def get_batch(self) -> list[ImagePrompt]:
        # todo Check that file is actually image in webp format
        return self._prompt_storage.get_batch(batch_size=self._batch_size)


image_prompt_manager = ImagePromptManager(
    batch_size=config.image_prompt_batch_size,
    prompt_storage=InMemoryImagePromptStorage(
        default_resources_dir=Path(config.default_image_prompt_dir),
        max_prompt_cnt=config.submitted_image_prompt_buffer_size,
    ),
)
