"""Модуль конфигурации Celery хендлеров"""
from typing import Any

import celery


class CeleryTaskHandler(celery.Task):
    """Выполняет определенные действия до старта, после завершения задачи и по ее результатам"""

    def before_start(self, task_id, args, kwargs):
        """Вызывается перед стартом задачи"""

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Вызывается после завершения задачи"""

    def on_failure(self, exc: Exception, task_id: str, args: list, kwargs: dict, einfo: Any):
        """
        Вызывается если выполнение задачи завершено с ошибкой (bultin метод celery)
        :param exc: Класс ошибки
        :param task_id: ID задачи celery
        :param args: Список параметров, переданных в задачу
        :param kwargs: Словарь из параметров, переданных в задачу
        :param einfo: Содержание ошибки
        """

    def on_success(self, retval: Any, task_id: str, args: list, kwargs: dict):
        """
        Вызывается, если выполнение задачи завершено успешно (bultin метод celery)
        :param retval: return, который вернула задача
        :param task_id: ID задачи celery
        :param args: Список параметров, переданных в задачу
        :param kwargs: Словарь из параметров, переданных в задачу
        """
