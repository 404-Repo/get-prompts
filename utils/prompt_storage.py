import asyncio
import os
import random as rd
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Generic, TypeVar

import aiofiles  # type: ignore
import bittensor as bt
from main.exceptions import FileWithTextDataDoesntExist, NoDefaultImagePrompts

from utils.schemas.image_prompt import ImagePrompt


PromptT = TypeVar("PromptT")


class BasePromptStorage(ABC, Generic[PromptT]):

    @abstractmethod
    def get_batch(self, *, batch_size: int) -> list[PromptT]:
        pass

    @abstractmethod
    def add(self, *, prompts: list[PromptT]) -> None:
        pass


class InMemoryTextPromptStorage(BasePromptStorage[str]):
    def __init__(self, *, max_text_cnt: int, file_path: Path | None = None) -> None:
        print("InMemoryTextPromptStorage init")
        self._max_prompt_cnt = max_text_cnt
        self._prompts: deque[str] = deque(maxlen=self._max_prompt_cnt)
        self._prompt_set = set()
        if file_path is not None:
            if not file_path.exists():
                raise FileWithTextDataDoesntExist(f"File {file_path} does not exist.")
            with file_path.open("r") as f:
                print(file_path)
                self._prompts = deque(f.readlines())
                self._prompt_set = set(self._prompts)
        bt.logging.info(f"{len(self._prompts)} prompts loaded")

    def get_batch(self, *, batch_size: int) -> list[str]:
        return rd.sample(list(self._prompts), min(len(self._prompts), batch_size))

    def add(self, *, prompts: list[str]) -> None:
        unique_prompts = (d for d in prompts if d not in self._prompt_set)
        unique_prompt_cnt = sum(1 for _ in unique_prompts)
        total_prompt_cnt = unique_prompt_cnt + len(self._prompts)
        if total_prompt_cnt > self._max_prompt_cnt:
            for _ in range(total_prompt_cnt - self._max_prompt_cnt):
                prompt = self._prompts.popleft()
                self._prompt_set.remove(prompt)
        self._prompts.extend(unique_prompts)
        self._prompt_set.update(unique_prompts)
        bt.logging.info(
            f"{unique_prompt_cnt} image prompts submitted. " f"Total count of prompts {len(self._prompts)}."
        )


class DiskImagePromptStorage(BasePromptStorage[ImagePrompt]):
    _FILE_CHUNK: int = 10

    def __init__(self, *, resources_dir: Path, min_prompt_cnt: int, max_concurrent_tasks_cnt: int) -> None:
        print("DiskImagePromptStorage init")
        self._resources_dir = resources_dir
        self._semaphor = asyncio.Semaphore(max_concurrent_tasks_cnt)
        if not self._resources_dir.exists():
            raise NoDefaultImagePrompts(f"{self._resources_dir} does not exist.")
        file_cnt = sum(1 for entry in os.scandir(self._resources_dir) if entry.is_file())
        if file_cnt < min_prompt_cnt:
            raise NoDefaultImagePrompts(
                f"There are {file_cnt} default images available " f"that is less than minimal amount {min_prompt_cnt}."
            )
        print("DiskImagePromptStorage done")

    async def get_batch(self, *, batch_size: int) -> list[ImagePrompt]:  # type: ignore
        file_paths = [f for f in self._resources_dir.iterdir()]
        selected_file_paths = rd.sample(file_paths, min(batch_size, len(file_paths)))

        async def read_file(file_path: Path) -> ImagePrompt:
            async with aiofiles.open(file_path, "rb") as f:
                return ImagePrompt(image_data=await f.read(), filename=file_path.name)

        async with self._semaphor:
            start_idx = 0
            end_idx = min(DiskImagePromptStorage._FILE_CHUNK, len(selected_file_paths))
            image_datas: list[ImagePrompt] = []
            proceed_load: bool = True
            while proceed_load:
                if end_idx >= len(selected_file_paths):
                    end_idx = len(selected_file_paths)
                    proceed_load = False
                chunk_image_datas = await asyncio.gather(
                    *(read_file(fp) for fp in selected_file_paths[start_idx:end_idx])
                )
                image_datas.extend(chunk_image_datas)
                start_idx = end_idx
                end_idx += DiskImagePromptStorage._FILE_CHUNK
            return image_datas

    def add(self, *, prompts: list[ImagePrompt]) -> None:
        raise NotImplementedError()


class InMemoryImagePromptStorage(BasePromptStorage[ImagePrompt]):
    def __init__(self, *, max_prompt_cnt: int) -> None:
        print("InMemoryImagePromptStorage init")
        self._max_prompt_cnt = max_prompt_cnt
        self._image_prompts: deque[ImagePrompt] = deque()
        self._filenames: set[str] = set()

    def get_batch(self, *, batch_size: int) -> list[ImagePrompt]:
        if len(self._image_prompts) < self._max_prompt_cnt:
            return rd.sample(self._image_prompts, min(len(self._image_prompts), batch_size))
        return list(self._image_prompts)

    def add(self, *, prompts: list[ImagePrompt]) -> None:
        unique_prompts = (im for im in prompts if im.filename not in self._filenames)
        unique_prompt_cnt = sum(1 for _ in unique_prompts)
        total_cnt = unique_prompt_cnt + len(self._image_prompts)
        if total_cnt > self._max_prompt_cnt:
            for _ in range(total_cnt - self._max_prompt_cnt):
                im = self._image_prompts.popleft()
                self._filenames.remove(im.filename)
        self._image_prompts.extend(unique_prompts)
        self._filenames.update(im.filename for im in unique_prompts)
        bt.logging.info(
            f"{unique_prompt_cnt} image prompts submitted. " f"Total count of prompts {len(self._image_prompts)}."
        )
