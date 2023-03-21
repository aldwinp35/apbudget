import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from api.cron import copy_budget_item, delete_old_job_executions

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            copy_budget_item,
            trigger=CronTrigger(day="1", month="*/1", hour="00", minute="00"),  # The 1st day of every month at midnight
            # trigger=CronTrigger(second="*/10"), # TEST: Every 10 second
            id=copy_budget_item.__name__,  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info(f"Added job {copy_budget_item.__name__}.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id=delete_old_job_executions.__name__,
            max_instances=1,
            replace_existing=True,
        )
        logger.info(f"Added weekly job: {delete_old_job_executions.__name__}")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
