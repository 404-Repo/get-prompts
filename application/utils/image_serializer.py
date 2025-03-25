import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from io import BytesIO

import msgpack
from fastapi import UploadFile

from application.config import config
from application.utils.prompt_storage import InMemoryImagePromptStorage, image_prompt_storage
from application.utils.schemas.image_prompt import ImagePrompt


_logger = logging.getLogger("uvicorn")


class BaseImagePromptSerializer(ABC):

    @abstractmethod
    async def serialize(self, *, imagePrompts: list[ImagePrompt]) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def deserialize(self, *, file: UploadFile) -> None:
        pass


class MessagePackImagePromptSerializer(BaseImagePromptSerializer):

    def __init__(self, *, image_prompt_storage: InMemoryImagePromptStorage, chunk_size: int = 1024 * 1024) -> None:
        self._chunk_size = chunk_size
        self._image_prompt_storage = image_prompt_storage

    async def serialize(self, *, image_prompts: list[ImagePrompt]) -> AsyncGenerator[bytes, None]:  # type: ignore
        data_stream = BytesIO()
        for prompt in image_prompts:
            data_stream.write(
                msgpack.packb(
                    {"normalized_prompt": prompt.normalized_prompt, "data": prompt.image_data},
                    use_bin_type=True,
                )
            )
        data_stream.seek(0)

        while True:
            chunk = data_stream.read(self._chunk_size)
            if not chunk:
                break
            await asyncio.sleep(0)
            yield chunk

    async def deserialize(self, *, file: UploadFile) -> None:
        unpacker = msgpack.Unpacker(raw=False)
        total_len = 0
        while True:
            chunk = await file.read(self._chunk_size)
            if not chunk:
                break

            unpacker.feed(chunk)
            image_prompts: list[ImagePrompt] = []
            for data in unpacker:
                normalized_prompt = data["normalized_prompt"]
                image_data = data["data"]
                image_prompts.append(
                    ImagePrompt(
                        normalized_prompt=normalized_prompt,
                        image_data=image_data,
                    )
                )
            if image_prompts:
                total_len += len(image_prompts)
                self._image_prompt_storage.add(prompts=image_prompts)


image_prompt_serializer = MessagePackImagePromptSerializer(
    chunk_size=config.image_prompt_chunk_size, image_prompt_storage=image_prompt_storage
)
