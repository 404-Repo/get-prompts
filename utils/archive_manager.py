import asyncio
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Iterable
from io import BytesIO

from utils.schemas.image_prompt import ImagePrompt


class BaseArchiveManager(ABC):

    @staticmethod
    @abstractmethod
    async def compress(*, image_prompts: Iterable[ImagePrompt]) -> BytesIO:
        pass

    @staticmethod
    @abstractmethod
    async def decompress(*, zip_data: BytesIO) -> Iterable[ImagePrompt]:
        pass


class ZipArchiveManager(BaseArchiveManager):
    @staticmethod
    async def compress(*, image_prompts: Iterable[ImagePrompt]) -> BytesIO:
        def write_zip() -> BytesIO:
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for data in image_prompts:
                    zip_file.writestr(data.filename, data.image_data.getvalue())
            buffer.seek(0)
            return buffer

        zip_buffer = await asyncio.to_thread(write_zip)
        return zip_buffer

    @staticmethod
    async def decompress(*, zip_data: BytesIO) -> list[ImagePrompt]:
        def extract_images_sync(zip_data: BytesIO) -> list[ImagePrompt]:
            prompts: list[ImagePrompt] = []
            with zipfile.ZipFile(zip_data, "r") as zip_ref:
                for file_name in zip_ref.namelist():
                    try:
                        with zip_ref.open(file_name) as file:
                            img_bytes = BytesIO(file.read())
                            prompts.append(
                                ImagePrompt(
                                    filename=file_name,
                                    image_data=img_bytes,
                                )
                            )
                    except Exception as e:
                        # todo logger
                        print(f"Failed to extract {file_name} from archive: {e}")
            return prompts

        return await asyncio.to_thread(extract_images_sync, zip_data)
