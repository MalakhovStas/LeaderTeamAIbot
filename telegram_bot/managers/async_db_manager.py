"""Модуль для автоматизации работы с БД"""
from datetime import datetime
from typing import Union, Tuple, Optional, Dict

from aiogram.types import Message, CallbackQuery
from loguru import logger

from ..config import ADMINS, TECH_ADMINS, DEBUG
from ..models import TelegramAccount
from users.models import User
from asgiref.sync import sync_to_async


class DBManager:
    """ Класс Singleton надстройка над ORM "peewee" для вынесения логики сохранения данных """
    __instance = None
    sign = None
    logger = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.sign = cls.__name__ + ': '
            cls.logger = logger
        return cls.__instance

    def __init__(self):
        self.logger = logger

    async def get_or_create_user(
            self,
            update: Union[Message, CallbackQuery]) -> Tuple[TelegramAccount, Union[bool, int]]:
        """ Если user_id не найден в таблице TelegramAccount -> создаёт новые записи в таблицах
        TelegramAccount по ключу user_id. Возвращает модель TelegramAccount и False, если
        пользователь существует в БД и модель TelegramAccount и int(кол-во пользователей в базе),
        если создан новый пользователь"""
        fact_create_and_num_users = False
        admin = True if update.from_user.id in set(tuple(map(
            int, ADMINS)) if ADMINS else tuple() + tuple(map(
                int, TECH_ADMINS)) if TECH_ADMINS else tuple()) else False
        user, fact_create = await TelegramAccount.objects.aget_or_create(
            tg_user_id=update.from_user.id)

        if fact_create:
            fact_create_and_num_users = await TelegramAccount.objects.acount()
            user.tg_username = update.from_user.username
            user.tg_first_name = update.from_user.first_name
            user.tg_last_name = update.from_user.last_name
            user.position = "admin" if admin else "user"
            user.password = "admin" if admin else None
            user.user = await User.objects.create_user(
                username=user.tg_username or user.tg_user_id, password=user.password)
            await user.asave()

        text = 'created new user' if fact_create else 'get user'
        if DEBUG:
            self.logger.debug(f'{self.sign} {text.upper()}: {user.tg_username=} | {user.user_id=}')
        return user, fact_create_and_num_users

    async def get_all_users(self, id_only: bool = False, not_ban: bool = False) -> Tuple:
        if not_ban and id_only:
            result = tuple(TelegramAccount.objects.filter(
                ban_from_user=0).all().values_list("tg_user_id", flat=True))
            if DEBUG:
                self.logger.debug(self.sign + f'func get_all_users -> selected all users_id WHERE '
                                              f'ban != ban num: {len(result) if result else None}')

        elif id_only:
            result = tuple(TelegramAccount.objects.all().values_list("tg_user_id", flat=True))
            if DEBUG:
                self.logger.debug(self.sign + f'func get_all_users -> selected all users_id '
                                              f'num: {len(result) if result else None}')

        else:
            result = tuple(TelegramAccount.objects.all())
            if DEBUG:
                self.logger.debug(self.sign + f'func get_all_users -> selected all users fields '
                                              f'num: {len(result) if result else None}')

        return result

    async def update_user_balance(
            self, user_id: str, up_balance: Optional[str] = None,
            down_balance: Optional[str] = None, zero_balance: bool = False) -> Union[Tuple, bool]:
        user = await TelegramAccount.objects.filter(tg_user_id=user_id).afirst()

        if not user:
            return False

        if up_balance and up_balance.isdigit():
            user.balance += int(up_balance)
        elif down_balance and down_balance.isdigit():
            user.balance -= int(down_balance)
        elif zero_balance:
            user.balance = 0
        else:
            return False, 'bad data'
        await user.asave()

        if up_balance:
            result = f'up_balance: {up_balance}'
        elif down_balance:
            result = f'down_balance: {down_balance}'
        else:
            result = f'zero_balance: {zero_balance}'
        if DEBUG:
            self.logger.debug(self.sign + f'{user_id=} | {result=} | new {user.balance=}')
        return True, user.balance, user.tg_username

    async def update_user_balance_requests(self, user_id: Union[str, int],
                                           up_balance: Optional[Union[str, int]] = None,
                                           down_balance: Optional[Union[str, int]] = None,
                                           zero_balance: bool = False) -> Union[Tuple, bool]:

        user = await TelegramAccount.objects.filter(tg_user_id=user_id).afirst()
        if not user:
            return False

        if up_balance and str(up_balance).isdigit():
            user.balance_requests += int(up_balance)
        elif down_balance and str(down_balance).isdigit():
            if user.balance_requests != 0:
                user.balance_requests -= int(down_balance)
            else:
                return False, 'not update user balance_requests=0'
        elif zero_balance:
            user.balance_requests = 0
        else:
            return False, 'bad data'
        await user.asave()

        if up_balance:
            result = f'up_balance: {up_balance}'
        elif down_balance:
            result = f'down_balance: {down_balance}'
        else:
            result = f'zero_balance: {zero_balance}'
        if DEBUG:
            self.logger.debug(self.sign + f'{user_id=} | {result=} | new {user.balance_requests=}')
        return True, user.balance_requests, user.tg_username

    async def update_user_access(
            self, user_id: Union[str, int], block: bool = False) -> Union[bool, Tuple]:

        user = await TelegramAccount.objects.filter(tg_user_id=user_id).afirst()
        if not user:
            return False
        if block:
            user.access = 'block'
        else:
            user.access = 'allowed'
        await user.asave()
        if DEBUG:
            self.logger.debug(self.sign + f'func update_user_access -> '
                                          f'{"BLOCK" if block else "ALLOWED"} '
                                          f'| user_id: {user_id}')
        return True, user.tg_username

    async def update_ban_from_user(
            self, update, ban_from_user: bool = False) -> Union[bool, tuple]:

        user = await TelegramAccount.objects.filter(tg_user_id=update.from_user.id).afirst()
        if not user:
            return False
        user.ban_from_user = ban_from_user
        await user.asave()
        if DEBUG:
            self.logger.debug(self.sign + f'func update_ban_from_user -> user: {user.tg_username} | '
                                          f'user_id: {update.from_user.id} | ban: {ban_from_user}')
        return True, user.tg_username

    async def count_users(
            self,
            all_users: bool = False,
            register: bool = False,
            date: Optional[datetime] = None) -> str:

        if all_users:
            nums = await TelegramAccount.objects.acount()
            if DEBUG:
                self.logger.debug(self.sign + f'func count_users -> all users {nums}')

        elif register:
            nums = await TelegramAccount.objects.filter(added_date=date).acount()
            if DEBUG:
                self.logger.debug(self.sign + 'func count_users -> num users: '
                                              f'{nums} WHERE date_join == date: {date}')

        else:
            nums = await TelegramAccount.objects.filter(date_last_request__gte=date).acount()
            if DEBUG:
                self.logger.debug(self.sign + f'func count_users -> num users: {nums} '
                                              f'WHERE date_last_request == date: {date}')
        return nums

    async def select_all_contacts_users(self) -> Tuple:
        users = tuple(TelegramAccount.objects.values(
            "tg_user_id", "tg_username", "first_name", "added_date",
            "date_last_request", "text_last_request", "num_requests", "ban_from_user").all())
        if not users:
            if DEBUG:
                self.logger.error(self.sign + 'BAD -> NOT users in DB')
        else:
            if DEBUG:
                self.logger.debug(self.sign + 'OK -> SELECT all contacts users -> '
                                              f'return -> {len(users)} users contacts')
        return users

    async def select_password(self, user_id: int) -> str:
        user = await TelegramAccount.objects.filter(tg_user_id=user_id).aget()

        if DEBUG:
            self.logger.debug(self.sign + 'func select_password password -> '
                                          f'len password {len(user.password)}')

        return user.password

    async def update_last_request_data(self, update, text_last_request: str) -> Optional[bool]:
        user = await TelegramAccount.objects.filter(tg_user_id=update.from_user.id).afirst()
        if not user:
            return False

        user.date_last_request = datetime.now()
        user.num_requests += 1
        user.text_last_request = text_last_request
        await user.asave()
        if DEBUG:
            self.logger.debug(self.sign + 'func update_last_request_data -> '
                                          f'user: {update.from_user.username} | '
                                          f'user_id:{update.from_user.id} | '
                                          f'last_request_data: {text_last_request}')
