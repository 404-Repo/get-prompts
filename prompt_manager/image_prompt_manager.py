import random as rd
from datetime import datetime
from pathlib import Path

from main.config import config
from main.exceptions import NoDefaultImagePrompts
from utils.archive_manager import ZstandardManager

from prompt_manager.base_prompt_manager import BasePromptManager
from prompt_manager.schemas.prompt_batch import ImagePromptBatch


class ImagePromptManager(BasePromptManager[ImagePromptBatch]):
    _DEFAULT_IMAGE_DIR: str = "default"
    _SUBMITTED_IMAGE_DIR: str = "submitted"
    _TEMP_DIR: str = "temp"

    def __init__(self, *, resources_dir: Path, batch_size: int) -> None:
        # todo Check that default directory exists and has at least batch_size elements.
        # todo Add common exception handler.
        # todo Cleanup cron job for the temp files in case of usual clean up failure.
        super().__init__(resources_dir=resources_dir, batch_size=batch_size)
        self._default_image_dir = self._resource_dir / self._DEFAULT_IMAGE_DIR
        if not self._default_image_dir.exists():
            raise NoDefaultImagePrompts(f"Default image directory does not exist: {self._default_image_dir}")

        self._submitted_image_dir = self._resource_dir / self._SUBMITTED_IMAGE_DIR
        self._submitted_image_dir.mkdir(parents=True, exist_ok=True)
        self._temp_dir = self._resource_dir / self._TEMP_DIR
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    async def submit(self, *, batch: ImagePromptBatch) -> None:
        # todo Check format of the uploaded images?
        await ZstandardManager.decompress(archive_path=batch.archive_path, output_dir=self._submitted_image_dir)
        batch.archive_path.unlink()

    async def get(self) -> ImagePromptBatch:
        # todo Check that file is actually image in webp format
        # todo Check that files are bigger than batch size
        files = [f for f in self._default_image_dir.iterdir()]
        files.extend([f for f in self._submitted_image_dir.iterdir()])
        batch_files = rd.sample(files, self._batch_size)
        archive_path = self.get_archive_path()
        await ZstandardManager.compress(files=batch_files, archive_path=archive_path)
        return ImagePromptBatch(archive_path=archive_path)

    def get_archive_path(self) -> Path:
        timestamp = datetime.now().timestamp()
        return self._temp_dir / f"{timestamp}.zst"


image_prompt_manager = ImagePromptManager(
    resources_dir=Path(config.image_resource_dir), batch_size=config.image_prompt_batch_size
)
