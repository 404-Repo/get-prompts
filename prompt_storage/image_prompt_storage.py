from pathlib import Path

import pandas as pd
from exceptions import FileWithTextDataDoesntExist, NotEnoughPromptsAvailable
from settings import settings
from prompt_storage.image_prompt import ImagePrompt
from prompt_storage.base_prompt_storage import BasePromptStorage


class ImagePromptStorage(BasePromptStorage[ImagePrompt]):
    """
    Saves in memory image prompts: urls in S3 compatible storage 
    and normalized text prompt per each image if they are available.
    """
    def __init__(
        self,
        *,
        storage_size: int,
        batch_size: int,
        default_prompt_file_path: Path,
    ) -> None:
        super().__init__(
            storage_size=storage_size, 
            batch_size=batch_size, 
            default_prompt_file_path=default_prompt_file_path,
        )

        if not default_prompt_file_path.exists():
            raise FileWithTextDataDoesntExist(f"File {default_prompt_file_path} does not exist.")
        with open(default_prompt_file_path, "r") as f:
            prompts = [ImagePrompt(url=line.strip()) for line in f.readlines()]
            self._all_prompts.update(prompts)
