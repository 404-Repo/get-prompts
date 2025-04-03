from abc import ABC, abstractmethod
from typing import Any


class BasePrompt(ABC):

    @abstractmethod
    async def submit(self, *, batch: Any) -> None:
        pass

    @abstractmethod
    async def get_batch(self, *, batch_size: int) -> Any:
        pass
