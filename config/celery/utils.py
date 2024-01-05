"""Модуль дополнительных инструментов для конфигурации Celery"""
from kombu import Queue, Exchange
from django.conf import settings


def route_tasks(name: str, args: list, kwargs: dict, options, task=None, **kw) -> dict:
    """Маршрутизатор задач, через него celery_task попадает
    в очередь в зависимости от gateway переданного в kwargs celery_task функции"""
    if task.name == "task1" and (gateway := kwargs.get("gateway")) in settings.GATEWAYS_NAMES:
        result = {
            "exchange": gateway,
            "exchange_type": "direct",
            "routing_key": gateway,
        }
    else:
        result = {
            "exchange": "default",
            "exchange_type": "direct",
            "routing_key": "default",
        }
    return result


def create_queues() -> list:
    """Создаёт список очередей, по количеству gateway в .env"""
    queues = [
        Queue(
            name="default",
            exchange=Exchange(name="default", type="direct"),
            routing_key="default",
        )
    ]
    for gateway_name in settings.GATEWAYS_NAMES:
        queues.append(
            Queue(
                name=gateway_name,
                exchange=Exchange(name=gateway_name, type="direct"),
                routing_key=gateway_name,
                queue_arguments={"x-max-priority": settings.X_MAX_PRIORITY},
            )
        )
    return queues
