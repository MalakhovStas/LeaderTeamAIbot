"""Модуль дополнительных инструментов конфигурации приложения"""
from art import tprint  # type: ignore
from colorama import Fore

from config.settings import DEBUG, PYPROJECT


def print_logo() -> None:
    """Приветственная заставка в консоли"""
    if DEBUG:
        print(Fore.LIGHTGREEN_EX)
        tprint(PYPROJECT['tool']['poetry']['description'])
        print(Fore.RESET)
