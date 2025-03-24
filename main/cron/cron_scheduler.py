import datetime as dt

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from main.cron.base_cron_job import BaseCronJob


class CronScheduler:
    """
    The utility class is used for managing and executing periodic tasks using AsyncIOScheduler.
    """

    _scheduler = AsyncIOScheduler()

    @classmethod
    def add_job(
        cls,
        *,
        job_type: type[BaseCronJob],
        id: str,
        trigger: str,
        hours: int = 0,
        minutes: int = 0,
        next_run_time: dt.datetime | None,
        misfire_grace_time: int | None,
    ) -> None:
        """The method registers a new job with specified parameters and execution logic."""
        cls._scheduler.add_job(
            func=job_type.execute,
            id=id,
            trigger=trigger,
            hours=hours,
            minutes=minutes,
            next_run_time=next_run_time,
            misfire_grace_time=misfire_grace_time,
        )

    @classmethod
    def start(cls) -> None:
        """The method starts the scheduler, enabling the execution of scheduled jobs."""
        cls._scheduler.start()

    @classmethod
    def shutdown(cls) -> None:
        """The method stops the scheduler, preventing further execution of scheduled jobs."""
        cls._scheduler.shutdown(wait=False)
