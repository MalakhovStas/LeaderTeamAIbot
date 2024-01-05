"""Модуль конфигурации задач Celery"""

from celery.utils.log import get_task_logger

from .config import app
from .handlers import CeleryTaskHandler

logger = get_task_logger(__name__)


@app.task(name='task', acks_late=True, base=CeleryTaskHandler)
def task(*args, **kwargs):
    ...
