import logging
import random as rd
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Generic, TypeVar

from application.config import config
from application.exceptions import FileWithTextDataDoesntExist, NoDefaultImagePrompts
from application.utils.schemas.image_prompt import ImagePrompt


PromptT = TypeVar("PromptT")

_logger = logging.getLogger("uvicorn")


class BasePromptStorage(ABC, Generic[PromptT]):

    @abstractmethod
    def get_batch(self, *, batch_size: int) -> list[PromptT]:
        pass

    @abstractmethod
    def add(self, *, prompts: list[PromptT]) -> None:
        pass


class InMemoryTextPromptStorage(BasePromptStorage[str]):
    def __init__(self, *, max_prompt_cnt: int, default_prompt_path: Path) -> None:
        self._prompts: deque[str] = deque(maxlen=max_prompt_cnt)
        self._all_prompts: set[str] = set()
        if not default_prompt_path.exists():
            raise FileWithTextDataDoesntExist(f"File {default_prompt_path} does not exist.")
        with default_prompt_path.open("r") as f:
            lines = [line.replace("\n", "") for line in f.readlines()]
            self._all_prompts.update(lines)
            self._prompts.extend(lines)

    @property
    def prompt_cnt(self) -> int:
        return len(self._prompts)

    def get_batch(self, *, batch_size: int) -> list[str]:
        return rd.sample(list(self._prompts), min(len(self._prompts), batch_size))

    def add(self, *, prompts: list[str]) -> None:
        prev_prompt_cnt = len(self._all_prompts)
        self._prompts.extend(prompts)
        self._all_prompts.update(prompts)
        new_prompt_cnt = len(self._all_prompts) - prev_prompt_cnt
        _logger.info(f"{len(prompts)} text prompts were submitted. New prompts: {new_prompt_cnt}.")


class InMemoryImagePromptStorage(BasePromptStorage[ImagePrompt]):
    def __init__(self, *, default_resources_dir: Path, max_prompt_cnt: int) -> None:
        self._image_prompts: deque[ImagePrompt] = deque(maxlen=max_prompt_cnt)
        if not default_resources_dir.exists():
            raise NoDefaultImagePrompts(f"{default_resources_dir} does not exist.")
        for file in default_resources_dir.iterdir():
            with file.open("rb") as f:
                self._image_prompts.append(ImagePrompt(image_data=f.read()))
            if len(self._image_prompts) == max_prompt_cnt:
                break
        _logger.info(f"In memory image storage was initialized by {len(self._image_prompts)} default prompts.")

    @property
    def prompt_cnt(self) -> int:
        return len(self._image_prompts)

    def get_batch(self, *, batch_size: int) -> list[ImagePrompt]:
        return rd.sample(self._image_prompts, min(len(self._image_prompts), batch_size))

    # todo Stream addition?
    def add(self, *, prompts: list[ImagePrompt]) -> None:
        _logger.info(f"{len(prompts)} image prompts were submitted.")
        self._image_prompts.extend(prompts)


image_prompt_storage = InMemoryImagePromptStorage(
    default_resources_dir=Path(config.default_image_prompt_dir),
    max_prompt_cnt=config.submitted_image_prompt_buffer_size,
)
