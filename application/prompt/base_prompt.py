from abc import ABC, abstractmethod
from typing import Any


class BasePrompt(ABC):

    @abstractmethod
    def submit(self, *, batch: Any) -> None:
        pass

    @abstractmethod
    def get_batch(self, *, batch_size: int) -> Any:
        pass
