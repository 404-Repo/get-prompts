from main.cron.base_cron_job import BaseCronJob
from main.dependencies import metagraph_manager


class SyncMetagraphCronJob(BaseCronJob):
    """The cron job class is responsible for verifying the database connection."""

    @classmethod
    async def _execute_impl(cls) -> None:
        await metagraph_manager.sync()
