import asyncio
import logging
import os

import psutil

from application.dependencies import metagraph_manager


_logger = logging.getLogger("uvicorn")
_SYNC_METAGRAPH_INTERVAL_SEC: int = 30 * 60
_SYNC_RAM_INTERVAL_SEC: int = 60


async def sync_metagraph_cron() -> None:
    while True:
        try:
            _logger.info("Sync metagraph")
            await metagraph_manager.sync()
            _logger.info("Sync metagraph done")
        except Exception as e:
            print(f"Sync metagraph failed: {e}")
        finally:
            await asyncio.sleep(_SYNC_METAGRAPH_INTERVAL_SEC)


async def sync_ram_cron() -> None:
    while True:
        try:
            _logger.info("Sync RAM")
            process = psutil.Process(os.getpid())  # Get current process
            mem_info = process.memory_info()
            rss = mem_info.rss / (1024 * 1024)  # Convert to MB
            vms = mem_info.vms / (1024 * 1024)  # Convert to MB
            _logger.info(f"RSS (Resident Set Size): {rss:.2f} MB")
            _logger.info(f"VMS (Virtual Memory Size): {vms:.2f} MB")
            _logger.info("Sync metagraph RAM")
        except Exception as e:
            print(f"Sync RAM failed: {e}")
        finally:
            await asyncio.sleep(_SYNC_METAGRAPH_INTERVAL_SEC)
