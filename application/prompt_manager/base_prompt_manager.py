from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from application.prompt_manager.schemas.prompt_batch import BasePromptBatch


BatchT = TypeVar("BatchT", bound=BasePromptBatch)


class BasePromptManager(ABC, Generic[BatchT]):
    def __init__(self, *, batch_size: int) -> None:
        self._batch_size: int = batch_size

    @abstractmethod
    async def submit(self, *, batch: BatchT) -> None:
        pass

    @abstractmethod
    async def get_batch(self) -> BatchT:
        pass
