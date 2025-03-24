from pathlib import Path

from main.config import config
from utils.prompt_storage import InMemoryImagePromptStorage

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


class ImagePromptManager(BasePromptManager[ImagePromptBatch]):
    def __init__(
        self,
        *,
        batch_size: int,
        submitted_image_storage: InMemoryImagePromptStorage,
    ) -> None:
        super().__init__(batch_size=batch_size)
        self._submitted_image_storage = submitted_image_storage

    def submit(self, *, image_batch: ImagePromptBatch) -> None:  # type: ignore
        self._submitted_image_storage.add(prompts=image_batch.image_prompts)

    async def get_batch(self) -> ImagePromptBatch:
        # todo Check that file is actually image in webp format
        image_datas = self._submitted_image_storage.get_batch(batch_size=self._batch_size)
        return ImagePromptBatch(
            image_prompts=image_datas,
        )


image_prompt_manager = ImagePromptManager(
    batch_size=config.image_prompt_batch_size,
    submitted_image_storage=InMemoryImagePromptStorage(
        default_resources_dir=Path(config.default_image_prompt_dir),
        max_prompt_cnt=config.submitted_image_prompt_buffer_size,
    ),
)
