from abc import ABC, abstractmethod
from typing import Generic, TypeVar


DataT = TypeVar("DataT")


class BasePromptManager(ABC, Generic[DataT]):
    def __init__(self, *, batch_size: int) -> None:
        self._batch_size: int = batch_size

    @abstractmethod
    async def submit(self, *, batch: list[DataT]) -> None:
        pass

    @abstractmethod
    async def get_batch(self) -> list[DataT]:
        pass
