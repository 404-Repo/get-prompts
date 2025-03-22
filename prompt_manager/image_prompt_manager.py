from main.config import config
from utils.data_storage import DiskImageStorage, InMemoryImageStorage

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


class ImagePromptManager(BasePromptManager[ImagePromptBatch]):
    def __init__(
        self, *, batch_size: int, default_image_storage: DiskImageStorage, submitted_image_storage: InMemoryImageStorage
    ) -> None:
        super().__init__(batch_size=batch_size)
        self._default_image_storage = default_image_storage
        self._submitted_image_storage = submitted_image_storage

    def submit(self, *, batch: ImagePromptBatch) -> None:  # type: ignore
        self._submitted_image_storage.add(datas=batch.image_datas)

    async def get(self) -> ImagePromptBatch:
        # todo Check that file is actually image in webp format
        image_datas = self._submitted_image_storage.get(batch_size=self._batch_size)
        if len(image_datas) < self._batch_size:
            add_image_cnt = self._batch_size - len(image_datas)
            default_images = await self._default_image_storage.get(batch_size=add_image_cnt)
            image_datas += default_images
        return ImagePromptBatch(
            image_datas=image_datas,
        )


image_prompt_manager = ImagePromptManager(
    batch_size=config.image_prompt_batch_size,
    default_image_storage=DiskImageStorage(
        resources_dir=config.image_prompt_resources_dir, min_default_file_cnt=config.image_prompt_batch_size
    ),
    submitted_image_storage=InMemoryImageStorage(
        max_image_cnt=config.submitted_image_prompt_buffer_size,
    ),
)
