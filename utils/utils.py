import os
import random
import re
import string
from datetime import datetime
from random import choice
from typing import Tuple, Union, Optional, Any

from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.utils import timezone
from loguru import logger


def get_fullname(search_query: str) -> Tuple:
    """Выделяет из строки имя, фамилию, отчество разделённые пробелом"""
    name, surname, patronymic = None, None, None
    if search_query:
        search_query = search_query.split(' ', maxsplit=2)
        if len(search_query) == 1 and '\n' in search_query[0]:
            search_query = search_query[0].split('\n', maxsplit=2)
        if 0 < len(search_query) <= 3 and all([word.isalpha() for word in search_query]):
            if len(search_query) == 3:
                name, surname, patronymic = search_query
            elif len(search_query) == 2:
                name, surname, patronymic = search_query[0], search_query[1], ''
            elif len(search_query) == 1:
                name, surname, patronymic = search_query[0], None, None
    name = name.lower().title() if isinstance(name, str) else name
    surname = surname.lower().title() if isinstance(surname, str) else surname
    patronymic = patronymic.lower().title() if isinstance(patronymic, str) else patronymic
    return name, surname, patronymic


def get_passport(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) == 10:
        result = search_query
    return result


def get_inn(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) == 12:
        result = search_query
    return result


def get_id_credit(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) < 10:
        result = search_query
    return result


def get_phone_number(search_query: str) -> Union[int, bool]:
    result = False
    search_query = search_query.replace(' ', '')
    if search_query.isdigit() and len(search_query) < 10:
        result = search_query
    return result


async def data_to_str_digits(data: str) -> Optional[str]:
    """Удаляет из строки data все символы из table_symbols на выходе только цифры или None"""
    ru_alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    en_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    any_symbols = ' ~`"\'@#№$:;.,%^&?*|()[]{}-=+<>/\\'
    table_symbols = ''.join([*ru_alphabet, *en_alphabet, *any_symbols])

    for sym in table_symbols:
        data = data.replace(sym, '')
    return data if data.isdigit() else None


async def data_to_phone(data: str) -> Optional[str]:
    """Выделяет из строки символов цифры проверяет их количество, если == 11,
    возвращает набор цифр, в противном случае None"""
    result = None
    numbers = await data_to_str_digits(data)
    if numbers and len(numbers) == 11:
        result = numbers
    return result


async def data_to_email(data: str) -> Optional[str]:
    """Проверяет email на соответствие паттерну регулярного выражения,
    возвращает введённый email, в противном случае None"""
    result = None
    # pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, data) is not None:
        result = data
    return result


def make_code_tg_register_link():
    """Формирует строку случайных неповторяющихся символов длиной length"""
    length = 32
    dictionary = string.digits + string.ascii_letters
    return "".join(random.sample(dictionary, length))


def get_key_from_value_dict(i_dict: dict, value: Any) -> Optional[Any]:
    """Возвращает ключ словаря по первому соответствующему значению"""
    for key, val in i_dict.items():
        if val == value:
            return key


def data_to_datetime(data: str) -> Optional[datetime]:
    """Преобразует строку data в объект Datetime с часовым поясом из настроек django и
    возвращает его, если строка соответствует формату 01.01.2024 12:00, иначе возвращает None"""
    date = None
    try:
        date = timezone.make_aware(
            datetime.strptime(data, settings.GENERAL_DATETIME_FORMAT_FOR_MESSAGE),
            timezone.get_current_timezone()
        ).astimezone(timezone.get_current_timezone())
    except ValueError as exc:
        logger.debug(f'{exc=} | return -> None')
    return date


def generate_random_string(length: int) -> str:
    """ Генерирует случайную строку длиной length из
        символов английского алфавита и цифр"""
    symbols = string.ascii_letters + string.digits
    return ''.join(choice(seq=symbols) for _ in range(length))


def create_invite_link(bot_username: str, referrer_id: int | str) -> str:
    """Создаёт и сохраняет в кэш реферальную ссылку с временем жизни==INVITE_LINK_LIFE"""
    invite_code = generate_random_string(35)
    settings.REDIS_CACHE.set(name=invite_code, value=referrer_id, ex=settings.INVITE_LINK_LIFE)
    return f"<a>https://t.me/{bot_username}?start={invite_code}&preview:true</a>"


async def create_keyboard(button: Any) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру из одной кнопки"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=button.name, callback_data=button.class_name))
    return keyboard


def check_or_create_directory(path: str) -> bool:
    """Создаёт директорию если её не существует"""
    if not (is_dir := os.path.isdir(path)):
        os.mkdir(path)
        return os.path.isdir(path)
    return is_dir
