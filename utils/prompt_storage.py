import logging
import os
import random as rd
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Generic, TypeVar

from main.exceptions import FileWithTextDataDoesntExist, NoDefaultImagePrompts, NotEnoughImages

from utils.schemas.image_prompt import ImagePrompt


PromptT = TypeVar("PromptT")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")


class BasePromptStorage(ABC, Generic[PromptT]):

    @abstractmethod
    def get_batch(self, *, batch_size: int) -> list[PromptT]:
        pass

    @abstractmethod
    def add(self, *, prompts: list[PromptT]) -> None:
        pass


class InMemoryTextPromptStorage(BasePromptStorage[str]):
    def __init__(self, *, max_text_cnt: int, file_path: Path | None = None) -> None:
        logger.info("In memory text storage init")
        self._max_prompt_cnt = max_text_cnt
        self._prompts: deque[str] = deque(maxlen=self._max_prompt_cnt)
        self._prompt_set = set()
        if file_path is not None:
            if not file_path.exists():
                raise FileWithTextDataDoesntExist(f"File {file_path} does not exist.")
            with file_path.open("r") as f:
                self._prompts = deque(f.readlines())
                self._prompt_set = set(self._prompts)
        logger.info(f"{len(self._prompts)} prompts loaded")

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
        logger.info(f"{unique_prompt_cnt} image prompts submitted. " f"Total count of prompts {len(self._prompts)}.")


class InMemoryImagePromptStorage(BasePromptStorage[ImagePrompt]):
    def __init__(self, *, default_resources_dir: Path, max_prompt_cnt: int) -> None:
        self._max_prompt_cnt = max_prompt_cnt
        self._image_prompts: deque[ImagePrompt] = deque()
        self._filenames: set[str] = set()
        if not default_resources_dir.exists():
            raise NoDefaultImagePrompts(f"{default_resources_dir} does not exist.")
        file_cnt = sum(1 for entry in os.scandir(default_resources_dir) if entry.is_file())
        if file_cnt < max_prompt_cnt:
            raise NoDefaultImagePrompts(
                f"There are {file_cnt} default images available " f"that is less than needed amount {max_prompt_cnt}."
            )
        files = list(default_resources_dir.iterdir())
        default_files = rd.sample(files, max_prompt_cnt)
        for file in default_files:
            with file.open("rb") as f:
                self._filenames.add(file.name)
                self._image_prompts.append(ImagePrompt(filename=file.name, image_data=f.read()))
        logger.info(f"In memory image storage was initialized by {len(self._image_prompts)} default prompts.")

    def get_batch(self, *, batch_size: int) -> list[ImagePrompt]:
        if batch_size > len(self._image_prompts):
            raise NotEnoughImages(f"{len(self._image_prompts)} images available but {batch_size} requested.")
        return rd.sample(self._image_prompts, batch_size)

    # todo Stream addition?
    def add(self, *, prompts: list[ImagePrompt]) -> None:
        unique_prompts = [im for im in prompts if im.filename not in self._filenames]
        unique_prompt_cnt = len(unique_prompts)
        total_cnt = unique_prompt_cnt + len(self._image_prompts)
        if total_cnt > self._max_prompt_cnt:
            for _ in range(total_cnt - self._max_prompt_cnt):
                im = self._image_prompts.popleft()
                self._filenames.remove(im.filename)
        self._image_prompts.extend(unique_prompts)
        self._filenames.update([im.filename for im in unique_prompts])
        logger.info(
            f"{unique_prompt_cnt=} image prompts submitted. " f"Total count of prompts {len(self._image_prompts)}."
        )
