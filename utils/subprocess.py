import subprocess

from colorama import Fore
from loguru import logger

from config import settings


def application_testing() -> None:
    """Запускает тестирование приложения в subprocess"""
    logger.debug('Start tests application ...')
    tests = subprocess.check_output(['bash', '-c', 'pytest src/tests'])
    logger.info(f"\n{tests.decode('utf-8')}")


# def start_gateways_celery_workers() -> None:
#     """Создаёт и запускает подпроцессы python с celery workers по одном для каждого шлюза(банка)"""
#     for gateway_name in settings.GATEWAYS_NAMES:
#         start_celery_worker_subprocess(gateway_name=gateway_name)
#
#
# def stop_gateways_celery_workers() -> None:
#     """Завершает работу всех celery workers всех шлюзов(банков)"""
#     print(f'{Fore.RED}Завершение работы Celery воркеров!{Fore.RESET}')
#     for gateway_name in settings.GATEWAYS_NAMES:
#         stop_celery_worker_subprocess(gateway_name=gateway_name)
#
#
# def start_celery_worker_subprocess(gateway_name: str) -> bool:
#     """Запуск подпроцессов celery_workers"""
#     result = False
#     if settings.GATEWAYS and gateway_name in settings.APP_CONFIG['gateways_workers'].keys():
#         command = ["celery", "-A", "config.celery.celery_config:app", "worker", "-l", "info",
#                    "-Q", f"{gateway_name}", "-n", f"{gateway_name}"]
#         if not settings.STDOUT_STDERR_WORKERS_TO_CONTROLLER:
#             celery_worker = subprocess.Popen(
#                 command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
#         else:
#             celery_worker = subprocess.Popen(command)
#         logger.info(f"Starting celery worker Python subprocess - "
#                     f"process id: {celery_worker.pid} | gateway: {celery_worker.args[-1]}")
#         result = settings.APP_CONFIG['gateways_workers'][gateway_name].append(celery_worker)
#     return result
#
#
# def stop_celery_worker_subprocess(gateway_name: str) -> bool:
#     """Завершение подпроцессов celery_workers"""
#     result = False
#     if gateway_workers := settings.APP_CONFIG['gateways_workers'].get(gateway_name):
#         for worker in gateway_workers:
#             worker.kill()
#             logger.info("Stop Python subprocess - Celery worker: "
#                         f"{worker.args[-1]} | process id: {worker.pid}")
#         settings.APP_CONFIG['gateways_workers'][gateway_name].clear()
#         result = True
#     return result
