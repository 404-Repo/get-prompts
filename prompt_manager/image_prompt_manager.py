from pathlib import Path

from main.config import config
from utils.prompt_storage import DiskImagePromptStorage, InMemoryImagePromptStorage

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


class ImagePromptManager(BasePromptManager[ImagePromptBatch]):
    def __init__(
        self,
        *,
        batch_size: int,
        default_image_storage: DiskImagePromptStorage,
        submitted_image_storage: InMemoryImagePromptStorage,
    ) -> None:
        super().__init__(batch_size=batch_size)
        self._default_image_storage = default_image_storage
        self._submitted_image_storage = submitted_image_storage

    def submit(self, *, image_batch: ImagePromptBatch) -> None:  # type: ignore
        self._submitted_image_storage.add(prompts=image_batch.image_prompts)

    async def get_batch(self) -> ImagePromptBatch:
        # todo Check that file is actually image in webp format
        image_datas = self._submitted_image_storage.get_batch(batch_size=self._batch_size)
        if len(image_datas) < self._batch_size:
            add_image_cnt = self._batch_size - len(image_datas)
            default_images = await self._default_image_storage.get_batch(batch_size=add_image_cnt)
            image_datas += default_images
        return ImagePromptBatch(
            image_prompts=image_datas,
        )


image_prompt_manager = ImagePromptManager(
    batch_size=config.image_prompt_batch_size,
    default_image_storage=DiskImagePromptStorage(
        resources_dir=Path(config.default_image_prompt_dir),
        min_prompt_cnt=config.image_prompt_batch_size,
        max_concurrent_tasks_cnt=config.max_concurrent_image_tasks,
    ),
    submitted_image_storage=InMemoryImagePromptStorage(
        max_prompt_cnt=config.submitted_image_prompt_buffer_size,
    ),
)
