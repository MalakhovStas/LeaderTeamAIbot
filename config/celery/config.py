"""Основной модуль конфигурации Celery"""
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

from .utils import create_queues, route_tasks

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Список путей к задачам celery
Imports = ['config.celery.tasks']

app = Celery("DjangoAiogramTgBot", include=Imports)

# переменные для CELERY начинаются с этого слова
app.config_from_object("django.conf:settings", namespace="CELERY")

# автоматический поиск задач в указанном пакете
app.autodiscover_tasks(packages=["config.celery.tasks"], force=True)

# хранение периодических задач
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

app.conf.update(
    result_backend="django-db",
    cache_backend="default",
    broker_url=settings.REDIS_URL,
    broker_transport_options={
        "priority_steps": list(range(1, settings.X_MAX_PRIORITY + 1)),
        "queue_order_strategy": "priority",
    },
    accept_content=['application/json'],
    task_queues=create_queues(),
    task_routes=route_tasks,
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_concurrency=1,  # количество воркеров
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    broker_connection_retry_on_startup=True,
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    # Сохраняет задачи из очереди на бэкенде, если воркер упал
    default_delivery_mode="persistent",
    
    # Класс планировщика периодических задач
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    # Словарь с расписанием периодических задач
    beat_schedule={
        "periodic-task": {
            "task": "periodic-task",  # название задачи
            "schedule": settings.TASK_INTERVAL,  # интервал запуска в секундах
        },
    }
)
