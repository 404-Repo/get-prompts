from abc import abstractmethod
from pathlib import Path

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


class ImagePromptManager(BasePromptManager[ImagePromptBatch]):
    _DEFAULT_IMAGE_DIR: str = "default"
    _SUBMITTED_IMAGE_DIR: str = "submitted"

    def __init__(self, *, resources_dir: Path, batch_size: int) -> None:
        super().__init__(resources_dir=resources_dir, batch_size=batch_size)
        self._default_image_dir = self._resource_dir / self._DEFAULT_IMAGE_DIR
        self._submitted_image_dir = self._resource_dir / self._SUBMITTED_IMAGE_DIR
        self._submitted_image_dir.mkdir(parents=True, exist_ok=True)

    def submit(self, *, batch: ImagePromptBatch) -> None:
        pass

    @abstractmethod
    def get(self) -> ImagePromptBatch:
        pass
