"""Модуль инструментов для работы приложения с библиотекой subprocess"""

# pylint: disable=consider-using-with

import subprocess

from colorama import Fore
from loguru import logger

from django.conf import settings
from config.celery.config import app

def application_testing() -> None:
    """Запускает тестирование приложения в subprocess"""
    logger.debug('Start tests application ...')
    tests = subprocess.check_output(['bash', '-c', 'pytest src/tests'])
    logger.info(f"\n{tests.decode('utf-8')}")


# def start_drivers_celery_workers() -> None:
#     """Создаёт и запускает подпроцессы python с celery workers по одному для каждого драйвера"""
#     for driver_prefix in settings.DRIVERS_PREFIXES:
#         if "NOT_ACTIVE" in settings.DRIVER_CONFIG.get_driver_statuses(  # type: ignore
#                 driver_prefix
#         ):
#             logger.warning(f"Driver: {driver_prefix}, has status NOT_ACTIVE. Cannot be beginning.")
#             continue
#         start_celery_worker_subprocess(driver_prefix=driver_prefix)
#
#
# def stop_drivers_celery_workers() -> None:
#     """Завершает работу всех celery workers всех драйверов"""
#     print(f'{Fore.RED}Завершение работы Celery воркеров!{Fore.RESET}')
#     for driver_prefix in settings.DRIVERS_PREFIXES:
#         stop_celery_worker_subprocess(driver_prefix=driver_prefix)
#
#
# def start_celery_worker_subprocess(driver_prefix: str) -> bool:
#     """Запуск подпроцессов celery_workers"""
#     result = False
#     # statuses = settings.DRIVER_CONFIG.get_driver_statuses(driver_prefix)
#     if import_drivers_allocator(
#             driver_prefix) and settings.DRIVER_CONFIG.check_init_driver(driver_prefix):
#         command = ["celery", "-A", "config.celery.config:app", "worker", "-l", "info",
#                    "-Q", f"{driver_prefix}", "-n", f"{driver_prefix}"]
#         if not settings.STDOUT_STDERR_WORKERS_TO_CONTROLLER:
#             celery_worker = subprocess.Popen(
#                 command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
#         else:
#             celery_worker = subprocess.Popen(command)  # pylint: disable = consider-using-with
#         logger.info(f"Starting Celery worker Python subprocess - "
#                     f"process id: {celery_worker.pid} | "
#                     f"driver: {Fore.LIGHTGREEN_EX}{celery_worker.args[-1]}{Fore.RESET}")
#         result = settings.DRIVER_CONFIG.add_driver_worker(driver_prefix, celery_worker)
#     return result
#
#
# def stop_celery_worker_subprocess(driver_prefix: str) -> bool:
#     """Завершение подпроцессов celery_workers"""
#     result = False
#     driver_workers = settings.DRIVER_CONFIG.get_driver_workers(driver_prefix)
#     if driver_workers:  # and settings.DRIVER_CONFIG.check_init_driver(driver_prefix):
#         for worker in driver_workers:
#             worker.kill()
#             logger.info("Stop Celery worker Python subprocess - "
#                         f"process id: {worker.pid} | "
#                         f"driver: {Fore.LIGHTMAGENTA_EX}{worker.args[-1]}{Fore.RESET}")
#         settings.DRIVER_CONFIG.clear_driver_workers(driver_prefix)
#         result = True
#     return result


def start_celery_periodic_tasks_worker_subprocess() -> None:
    """Запуск подпроцесса celery_worker для периодических задач"""
    # FIXME разобраться почем на сервере не запускается worker
    # FileNotFoundError: [Errno 2] No such file or directory: 'celery'
    # nano telegram_bot / management / commands / start_tg_bot.py
    # journalctl -n 100 -f -u LeaderTeamAIbot-Development

    command = [
        "celery", "-A", "config.celery.config:app", "worker", "-B", '-l', 'info', "-Q", "default",
        "-n", "periodic_tasks_worker"
    ]
    if not settings.STDOUT_STDERR_WORKERS_TO_CONSOLE:
        celery_worker = subprocess.Popen(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    else:
        subprocess.Popen(['pwd'])
        celery_worker = subprocess.Popen(command)
    settings.APP_CONFIG['periodic_tasks_workers'].append(celery_worker)


def stop_celery_periodic_tasks_workers_subprocess() -> bool:
    """Завершение подпроцессов celery_workers для периодических задач"""
    result = False
    if periodic_tasks_workers := settings.APP_CONFIG['periodic_tasks_workers']:
        for worker in periodic_tasks_workers:
            worker.kill()
            subprocess.Popen(['killall', '-s', '9', 'celery'])
            logger.info("Stop Celery periodic_tasks_worker Python subprocess - "
                        f"process id: {worker.pid}")
        settings.APP_CONFIG['periodic_tasks_workers'].clear()
        result = True
    return result
