"""Модуль конфигурации задач Celery"""
import asyncio

from celery.utils.log import get_task_logger

from telegram_bot.utils.sending_calendar_event_reminders import (
    send_calendar_event_reminder_from_reminder)
from .config import app
from .handlers import CeleryTaskHandler

logger = get_task_logger(__name__)


@app.task(name='periodic.task_calendar_event_reminder', acks_late=True, base=CeleryTaskHandler)
def task_calendar_event_reminder(*args, **kwargs):
    """Периодическая задача для отправки напоминаний о событиях календаря компаний их участникам"""
    asyncio.get_event_loop().run_until_complete(send_calendar_event_reminder_from_reminder())
