import logging
import random as rd
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Any

import pandas as pd

from application.config import config
from application.exceptions import FileWithTextDataDoesntExist, NotEnoughPromptsAvailable


_logger = logging.getLogger("uvicorn")


class BasePromptStorage(ABC):

    @abstractmethod
    def get_batch(self, *, batch_size: int) -> Any:
        pass

    @abstractmethod
    def add(self, *, prompts: Any) -> None:
        pass


class InMemoryTextPromptStorage(BasePromptStorage):
    """
    Saves in memory text prompts.
    _prompts queue contains active prompts that are submitted by user.
    _all_prompts contains all prompts in general.
    """

    def __init__(self, *, max_prompt_cnt: int, default_prompt_file_path: Path) -> None:
        self._prompts: deque[str] = deque(maxlen=max_prompt_cnt)
        self._all_prompts: set[str] = set()
        if not default_prompt_file_path.exists():
            raise FileWithTextDataDoesntExist(f"File {default_prompt_file_path} does not exist.")
        with default_prompt_file_path.open("r") as f:
            lines = [line.replace("\n", "") for line in f.readlines()]
            self._all_prompts.update(lines)

    @property
    def prompt_cnt(self) -> int:
        """
        Returns number of submitted prompts.
        """
        return len(self._prompts)

    def get_batch(self, *, batch_size: int) -> list[str]:
        """
        Randomly extracts batch_size prompts from active prompts.
        If there are not enough active prompts than takes prompts from the all_prompts.
        """
        if batch_size > self.prompt_cnt + len(self._all_prompts):
            raise NotEnoughPromptsAvailable(
                f"You requested {batch_size} active prompts but only "
                f"{self.prompt_cnt + len(self._all_prompts)} active prompts available."
            )

        if batch_size == self.prompt_cnt:
            return list(self._prompts)
        elif batch_size > self.prompt_cnt:
            return list(rd.sample(self._prompts, batch_size))
        else:
            additional_prompt_cnt = batch_size - self.prompt_cnt
            batch_prompts = list(self._prompts)
            batch_prompts.extend(rd.sample(list(self._all_prompts), additional_prompt_cnt))
            return batch_prompts

    def add(self, *, prompts: list[str]) -> None:
        prev_prompt_cnt = len(self._all_prompts)
        self._prompts.extend(prompts)
        self._all_prompts.update(prompts)
        new_prompt_cnt = len(self._all_prompts) - prev_prompt_cnt
        _logger.info(f"{len(prompts)} text prompts were submitted. New prompts: {new_prompt_cnt}.")


class InMemoryImageUrlStorage(BasePromptStorage):
    """
    Saves in memory image urls in S3 compatible storage and prompt per each image.
    It is expected that storage is initialized from csv file containing
    two columns with url and normalized prompt.

    _urls queue contains active urls.
    _url_to_prompt contains all historical urls.
    """

    def __init__(self, *, max_url_cnt: int, default_image_url_file_path: Path) -> None:
        self._urls: deque[str] = deque(maxlen=max_url_cnt)
        self._url_to_prompt: dict[str, str] = dict()
        if not default_image_url_file_path.exists():
            raise FileWithTextDataDoesntExist(f"File {default_image_url_file_path} does not exist.")
        df = pd.read_csv(default_image_url_file_path)
        self._url_to_normalized_prompt = df.set_index(df.columns[0])[df.columns[1]].to_dict()

    @property
    def url_cnt(self) -> int:
        return len(self._urls)

    def get_batch(self, *, batch_size: int) -> dict[str, str]:
        """
        Randomly extracts batch_size image urls with normalized prompts from submitted image urls.
        If there are not enough active image urls than takes urls from the _url_to_normalized_prompt.
        """
        if batch_size > self.url_cnt + len(self._url_to_normalized_prompt):
            raise NotEnoughPromptsAvailable(
                f"You requested {batch_size} active urls but only "
                f"{self.url_cnt + len(self._url_to_normalized_prompt)} active urls available."
            )

        if batch_size == self.url_cnt:
            return {url: self._url_to_normalized_prompt[url] for url in self._urls}
        elif batch_size > self.url_cnt:
            batch_urls = rd.sample(self._urls, batch_size)
            return {url: self._url_to_normalized_prompt[url] for url in batch_urls}
        else:
            additional_prompt_cnt = batch_size - self.url_cnt
            url_to_normalized_prompt = {url: self._url_to_normalized_prompt[url] for url in self._urls}
            url_to_normalized_prompt.update(
                dict(rd.sample(self._url_to_normalized_prompt.items(), additional_prompt_cnt))
            )
            return url_to_normalized_prompt

    def add(self, *, prompts: dict[str, str]) -> None:
        """
        Adds new image url prompts to the storage.
        :param prompts: dictionary where key is an url of image in S3-compatible storage and value is normalized prompt.
        """
        prev_prompt_cnt = len(self._url_to_normalized_prompt)
        self._urls.extend(prompts.keys())
        self._url_to_normalized_prompt.update(prompts)
        new_prompt_cnt = len(self._url_to_normalized_prompt) - prev_prompt_cnt
        _logger.info(f"{len(prompts)} image urls were submitted. New prompts: {new_prompt_cnt}.")


text_prompt_storage = InMemoryTextPromptStorage(
    max_prompt_cnt=config.text_prompt_storage_size,
    default_prompt_file_path=config.default_text_prompt_file,
)
image_url_storage = InMemoryImageUrlStorage(
    max_url_cnt=config.image_url_storage_size, default_image_url_file_path=config.default_image_url_file
)
