import asyncio
import logging

from api.dependencies import metagraph


_logger = logging.getLogger("uvicorn")
_SYNC_METAGRAPH_INTERVAL_SEC: int = 30 * 60


async def sync_metagraph_cron() -> None:
    while True:
        try:
            await sync_metagraph()
        except Exception as e:
            _logger.info(f"Sync metagraph failed: {e}")
        finally:
            await asyncio.sleep(_SYNC_METAGRAPH_INTERVAL_SEC)


async def sync_metagraph() -> None:
    _logger.info("Sync metagraph")
    await metagraph.sync()
    _logger.info("Sync metagraph done")
    