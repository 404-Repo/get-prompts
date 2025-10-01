from pathlib import Path
import logging
import random as rd
from collections import deque
from exceptions import NotEnoughPromptsAvailable


_logger = logging.getLogger("uvicorn")


class PromptStorage:
    def __init__(self, *, storage_size: int, batch_size: int, default_prompt_file_path: Path) -> None:
        self._storage_size = storage_size
        """Maximal number of the latest generated prompts saved in storage"""
        self._batch_size = batch_size
        """Number of prompts to return from storage in batch"""
        self._prompts: deque[str] = deque(maxlen=storage_size)
        """Contains only the latest generated prompts"""
        self._all_prompts: set[str] = set()
        """Generated for all time prompts + default prompts"""

        if not default_prompt_file_path.exists():
            raise FileWithTextDataDoesntExist(f"File {default_prompt_file_path} does not exist.")
        with default_prompt_file_path.open("r") as f:
            prompts = [line.strip() for line in f.readlines()]
            self._all_prompts.update(prompts)

    @property
    def prompt_count(self) -> int:
        """Returns number of active submitted prompts."""
        return len(self._prompts)

    @property
    def all_prompt_count(self) -> int:
        """Returns number of all submitted prompts"""
        return len(self._all_prompts)

    def get_batch(self) -> list[str]:
        """
        Randomly extracts prompts from active prompts.
        If there are not enough active prompts than takes prompts from the all_prompts.
        """
        prompt_count = len(self._prompts)
        if self._batch_size > prompt_count + len(self._all_prompts):
            raise NotEnoughPromptsAvailable(
                f"You requested {self._batch_size} active prompts but only "
                f"{prompt_count + len(self._all_prompts)} active prompts available."
            )

        if self._batch_size == prompt_count:
            return list(self._prompts)
        elif self._batch_size < prompt_count:
            return list(rd.sample(self._prompts, self._batch_size))
        else:
            additional_prompt_count = self._batch_size - prompt_count
            batch_prompts = list(self._prompts)
            batch_prompts.extend(rd.sample(list(self._all_prompts), additional_prompt_count))
            return batch_prompts

    def add(self, *, prompts: list[str]) -> None:
        prev_prompt_count = len(self._all_prompts)
        self._prompts.extend(prompts)
        self._all_prompts.update(prompts)
        new_prompt_count = len(self._all_prompts) - prev_prompt_count
        _logger.info(f"{len(prompts)} text prompts were submitted. New prompts: {new_prompt_count}.")
