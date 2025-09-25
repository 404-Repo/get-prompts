from pathlib import Path
import logging
from typing import Generic
import random as rd
from collections import deque
from typing import TypeVar
from exceptions import NotEnoughPromptsAvailable


_logger = logging.getLogger("uvicorn")


T = TypeVar("T")


class BasePromptStorage(Generic[T]):
    def __init__(self, *, storage_size: int, batch_size: int, default_prompt_file_path: Path) -> None:
        self._storage_size = storage_size
        """Maximal number of the latest generated prompts saved in storage"""
        self._batch_size = batch_size
        """Number of prompts to return from storage in batch"""
        self._prompts: deque[T] = deque(maxlen=storage_size)
        """Contains only the latest generated prompts"""
        self._all_prompts: set[T] = set()
        """Generated for all time prompts + default prompts"""

    @property
    def prompt_cnt(self) -> int:
        """Returns number of active submitted prompts."""
        return len(self._prompts)

    @property
    def all_prompt_cnt(self) -> int:
        """Returns number of all submitted prompts"""
        return len(self._all_prompts)

    def get_batch(self) -> list[T]:
        """
        Randomly extracts prompts from active prompts.
        If there are not enough active prompts than takes prompts from the all_prompts.
        """
        prompt_cnt = len(self._prompts)
        if self._batch_size > prompt_cnt + len(self._all_prompts):
            raise NotEnoughPromptsAvailable(
                f"You requested {self._batch_size} active prompts but only "
                f"{prompt_cnt + len(self._all_prompts)} active prompts available."
            )

        if self._batch_size == prompt_cnt:
            return list(self._prompts)
        elif self._batch_size < prompt_cnt:
            return list(rd.sample(self._prompts, self._batch_size))
        else:
            additional_prompt_cnt = self._batch_size - prompt_cnt
            batch_prompts = list(self._prompts)
            batch_prompts.extend(rd.sample(list(self._all_prompts), additional_prompt_cnt))
            return batch_prompts

    def add(self, *, prompts: list[T]) -> None:
        prev_prompt_cnt = len(self._all_prompts)
        self._prompts.extend(prompts)
        self._all_prompts.update(prompts)
        new_prompt_cnt = len(self._all_prompts) - prev_prompt_cnt
        _logger.info(f"{len(prompts)} text prompts were submitted. New prompts: {new_prompt_cnt}.")
