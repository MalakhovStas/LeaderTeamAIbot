import asyncio

from django.core.management.base import BaseCommand

from telegram_bot import main
from utils import subprocess


class Command(BaseCommand):
    help = 'Command for launching a Telegram bot.'

    def handle(self, *args, **kwargs):
        try:
            subprocess.start_celery_periodic_tasks_worker_subprocess()
            asyncio.run(main.start())
        except BaseException as exc:
            subprocess.stop_celery_periodic_tasks_workers_subprocess()
            raise exc
