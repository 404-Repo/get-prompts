import asyncio
import logging

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
            _logger.info("Sync metagraph")
            await metagraph_manager.sync()
            _logger.info("Sync metagraph done")
        except Exception as e:
            print(f"Sync metagraph failed: {e}")
        finally:
            await asyncio.sleep(_SYNC_METAGRAPH_INTERVAL_SEC)
