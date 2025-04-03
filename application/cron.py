import asyncio
import logging

from application.dependencies import metagraph


_logger = logging.getLogger("uvicorn")
_SYNC_METAGRAPH_INTERVAL_SEC: int = 30 * 60


async def sync_metagraph_cron() -> None:
    while True:
        try:
            _logger.info("Sync metagraph")
            await metagraph.sync()
            _logger.info("Sync metagraph done")
        except Exception as e:
            _logger.info(f"Sync metagraph failed: {e}")
        finally:
            await asyncio.sleep(_SYNC_METAGRAPH_INTERVAL_SEC)
