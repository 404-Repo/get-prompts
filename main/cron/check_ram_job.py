import logging
import os

import psutil

from main.cron.base_cron_job import BaseCronJob


_logger = logging.getLogger("uvicorn")


class CheckRAMCronJob(BaseCronJob):
    """The cron job class is responsible for verifying the database connection."""

    @classmethod
    async def _execute_impl(cls) -> None:
        pid = os.getpid()
        process = psutil.Process(pid)
        memory_info = process.memory_info()
        _logger.info(f"RSS (Resident Set Size): {memory_info.rss / (1024 * 1024)} MB")
        _logger.info(f"VMS (Virtual Memory Size): {memory_info.vms / (1024 * 1024)} MB")
