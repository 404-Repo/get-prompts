import asyncio
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path

from utils.schemas.image_data import ImageData


class BaseArchiveManager(ABC):

    @staticmethod
    @abstractmethod
    async def compress(*, files: list[Path], archive_path: Path) -> None:
        pass

    @staticmethod
    @abstractmethod
    async def decompress(*, zip_data: BytesIO) -> Iterable[ImageData]:
        pass


class ZipArchiveManager(BaseArchiveManager):
    @staticmethod
    async def compress(*, files: list[Path], archive_path: Path) -> None:
        raise NotImplementedError

    @staticmethod
    async def decompress(*, zip_data: BytesIO) -> list[ImageData]:
        def extract_images_sync(zip_data: BytesIO) -> list[ImageData]:
            images: list[ImageData] = []
            with zipfile.ZipFile(zip_data, "r") as zip_ref:
                for file_name in zip_ref.namelist():
                    try:
                        with zip_ref.open(file_name) as file:
                            img_bytes = BytesIO(file.read())
                            images.append(
                                ImageData(
                                    filename=file_name,
                                    data=img_bytes,
                                )
                            )
                    except Exception as e:
                        # todo logger
                        print(f"Failed to extract {file_name} from archive: {e}")
            return images

        return await asyncio.to_thread(extract_images_sync, zip_data)
