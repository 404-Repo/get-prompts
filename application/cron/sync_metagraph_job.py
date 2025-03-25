from application.cron.base_cron_job import BaseCronJob
from application.dependencies import metagraph_manager


class SyncMetagraphJob(BaseCronJob):
    """The cron job class is responsible for verifying the database connection."""

    @classmethod
    async def _execute_impl(cls) -> None:
        await metagraph_manager.sync()
