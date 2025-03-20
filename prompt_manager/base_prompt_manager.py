from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from prompt_manager.schemas.prompt_batch import BasePromptBatch


BatchT = TypeVar("BatchT", bound=BasePromptBatch)


class BasePromptManager(ABC, Generic[BatchT]):
    def __init__(self, *, resources_dir: Path, batch_size: int) -> None:
        self._batch_size: int = batch_size
        self._resource_dir: Path = resources_dir

    @abstractmethod
    def submit(self, *, batch: BatchT) -> None:
        pass

    @abstractmethod
    def get(self) -> BatchT:
        pass
