import logging
from abc import ABC, abstractmethod


_logger = logging.getLogger("uvicorn")


class BaseCronJob(ABC):
    """The base class for provides a consistent structure for cron jobs operations."""

    @classmethod
    async def execute(cls) -> None:
        """The method executes the cron job."""
        try:
            _logger.info(f"{cls.__name__} started")
            await cls._execute_impl()
            _logger.info(f"{cls.__name__} finished")
        except Exception as e:
            _logger.info(f"{cls.__name__} failed. Error: {e}")

    @classmethod
    @abstractmethod
    async def _execute_impl(cls) -> None:
        """The method defines the specific job logic."""
        pass
