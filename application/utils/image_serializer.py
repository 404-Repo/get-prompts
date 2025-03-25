import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

import msgpack
from fastapi import UploadFile

from application.config import config
from application.utils.schemas.image_prompt import ImagePrompt


class BaseImagePromptSerializer(ABC):

    @abstractmethod
    async def serialize(self, *, imagePrompts: list[ImagePrompt]) -> AsyncGenerator[bytes, None]:
        pass

    @abstractmethod
    async def deserialize(self, *, file: UploadFile) -> list[ImagePrompt]:
        pass


class MessagePackImagePromptSerializer(BaseImagePromptSerializer):

    def __init__(self, *, chunk_size: int = 1024 * 1024) -> None:
        self._chunk_size = chunk_size

    # normalized_prompt
    async def serialize(self, *, image_prompts: list[ImagePrompt]) -> AsyncGenerator[bytes, None]:  # type: ignore
        for prompt in image_prompts:
            packed_data = msgpack.packb(
                {"normalized_prompt": prompt.normalized_prompt, "data": prompt.image_data}, use_bin_type=True
            )

            for i in range(0, len(packed_data), self._chunk_size):
                await asyncio.sleep(0)
                yield packed_data[i : i + self._chunk_size]

    async def deserialize(self, *, file: UploadFile) -> list[ImagePrompt]:
        unpacker = msgpack.Unpacker(raw=False)
        image_prompts: list[ImagePrompt] = []
        while True:
            chunk = await file.read(self._chunk_size)
            if not chunk:
                break

            unpacker.feed(chunk)
            for data in unpacker:
                for item in data:
                    normalized_prompt = item["normalized_prompt"]
                    image_data = item["data"]
                    image_prompts.append(
                        ImagePrompt(
                            normalized_prompt=normalized_prompt,
                            image_data=image_data,
                        )
                    )
        return image_prompts


image_prompt_serializer = MessagePackImagePromptSerializer(
    chunk_size=config.image_prompt_chunk_size,
)
