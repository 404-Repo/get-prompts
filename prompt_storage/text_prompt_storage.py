import logging
import random as rd
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Any

import pandas as pd

from settings import settings
from exceptions import FileWithTextDataDoesntExist, NotEnoughPromptsAvailable
from prompt_storage.base_prompt_storage import BasePromptStorage


_logger = logging.getLogger("uvicorn")


class TextPromptStorage(BasePromptStorage[str]):
    """
    Saves in memory text prompts.
    Contains queue with the latest generated prompts.
    If there are enough prompts then randomly selects prompts from this queue.
    If there are not enough prompts then uses selects prompts from all time generated prompts.
    It also contains default prompts in order to have smth to return after initialization.
    """

    def __init__(self, *, storage_size: int, batch_size: int, default_prompt_file_path: Path) -> None:
        super().__init__(
            storage_size=storage_size, 
            batch_size=batch_size, 
            default_prompt_file_path=default_prompt_file_path,
        )

        if not default_prompt_file_path.exists():
            raise FileWithTextDataDoesntExist(f"File {default_prompt_file_path} does not exist.")
        with default_prompt_file_path.open("r") as f:
            prompts = [line.strip() for line in f.readlines()]
            self._all_prompts.update(prompts)
