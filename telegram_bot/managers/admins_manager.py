""""Модуль методов доступных только администраторам"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Tuple

import openpyxl
import psutil
from aiogram.types import Message
from aiogram.utils.exceptions import BotBlocked, UserDeactivated, ChatNotFound

from users.models import User
from ..buttons_and_messages.base_classes import Base
from ..config import ADMINS, TECH_ADMINS, DEBUG
from ..logger_config import PATH_FILE_DEBUG_LOGS, PATH_FILE_ERRORS_LOGS
from ..utils import admins_send_message
from ..utils.states import FSMAdminStates


class AdminsManager:
    """ Класс Singleton для работы с кабинетом администратора и соблюдения принципа DRY """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, bot, logger, dbase, rm):
        self.sign = self.__class__.__name__ + ': '
        self.bot = bot
        self.logger = logger
        self.dbase = dbase
        self.requests_manager = rm
        self.admins = tuple(map(int, ADMINS)) if ADMINS else tuple()
        self.tech_admins = tuple(map(int, TECH_ADMINS)) if TECH_ADMINS else tuple()

    @staticmethod
    async def split_users_list(users_list, step=30) -> List:
        """Формирует список пользователей"""
        len_list = len(users_list)
        result = []

        if len_list <= step:
            result.append(users_list)
        else:
            for start in range(len_list)[::step]:
                stop = start + step
                result.append(users_list[start:stop])
        return result

    async def admin_commands(self, message) -> Tuple:
        """Основной обработчик команд администратора"""
        command: str = message.get_command()

        if not (message.from_user.id in self.admins or message.from_user.id in self.tech_admins):
            return None, None, None

        text, next_state, type_result = None, None, None
        text = (
            '<b>Команды администратора:</b>\n'
            '<b>/commands</b> - список команд\n'
            '<b>/my_id</b> - мой id\n'
            '<b>/how_users</b> - кол-во пользователей в базе\n'
            '<b>/stat</b> - статистика по пользователям\n'
            '<b>/users_info</b> - выгрузка детальной информации о пользователях\n'
            '<b>/mailing</b> - рассылка пользователям бота\n'
            '<b>/mailing_admins</b> - рассылка администраторам бота\n'
            '<b>/block_user</b> - заблокировать пользователя\n'
            '<b>/unblock_user</b> - разблокировать пользователя\n'
            '<b>/load_stat</b> - нагрузка на сервер\n'
            # '<b>/change_user_requests_balance</b> - изменить баланс ответов пользователя\n'
            # '<b>/unload_payment_data_user</b> - выгрузить данные по оплатам пользователя\n'
            # '<b>/check_proxies</b> - проверить прокси\n'
            # f'<b>/change_user_balance</b> - изменить баланс пользователя\n'
            # '<b>/unloading_logs</b> - выгрузка логов'

        )
        if message.from_user.id in self.tech_admins:
            text += (
                '<b>/unloading_logs</b> - выгрузка логов\n'
            )

        if command == '/commands':
            pass

        elif command == '/my_id':
            text = f'Твой id: {message.from_user.id}'

        elif command == '/mailing_admins':
            text = f'Введите сообщение для рассылки администраторам:'
            next_state = FSMAdminStates.mailing_admins

        elif command == '/mailing':
            text = f'Введите пароль:'
            next_state = FSMAdminStates.password_mailing

        elif command in ['/block_user', '/unblock_user']:
            text = '<b>Введите id пользователя:</b>'
            next_state = FSMAdminStates.block_user if command == '/block_user' \
                else FSMAdminStates.unblock_user

        elif command == '/change_user_balance':
            text = ('<b>Введите id пользователя и через пробел '
                    '+сумму на которую хотите увеличить его баланс,'
                    ' или -сумму на которую хотите уменьшить, для обнуления баланса введите 0</b>'
                    )
            next_state = FSMAdminStates.change_user_balance

        elif command == '/change_user_requests_balance':
            text = (
                '<b>Введите id пользователя и через пробел '
                '+сумму на которую хотите увеличить его баланс,'
                ' или -сумму на которую хотите уменьшить, для обнуления баланса введите 0</b>'
            )
            next_state = FSMAdminStates.change_user_requests_balance

        elif command == '/unloading_logs':
            await self.bot.send_document(
                chat_id=message.from_user.id, document=open(PATH_FILE_DEBUG_LOGS, 'rb'))
            await self.bot.send_document(
                chat_id=message.from_user.id, document=open(PATH_FILE_ERRORS_LOGS, 'rb'))
            if DEBUG:
                self.logger.debug(self.sign + f'OK -> send logs files -> user: '
                                              f'{message.from_user.id}, username: '
                                              f'{message.from_user.username}'
                                  )
            text = '<b>Файлы с логами отправлены</b>'

        elif command == '/unload_payment_data_user':
            text = '<b>Введите id пользователя:</b>'
            next_state = FSMAdminStates.unload_payment_data_user

        elif command == '/load_stat':
            text = await self.load_stat()

        elif command == '/check_proxies':
            text = await self.check_proxies()

        else:
            num_users = await self.dbase.count_users(all_users=True)
            num_users_active_from_24hours = await self.dbase.count_users(
                date=datetime.now().replace(microsecond=0) - timedelta(hours=24))
            num_users_active_from_week = await self.dbase.count_users(
                date=datetime.now().date() - timedelta(days=7))

            if command == '/how_users':
                text = f'В базе: {num_users} пользователей'

            elif command == '/stat':
                line = ''
                new_users_in_month = 0

                for day in range(datetime.now().date().day, 0, -1):
                    new_users_in_day = await self.dbase.count_users(
                        register=True,
                        date=datetime.now().date() - timedelta(days=day - 1)
                    )
                    new_users_in_month += new_users_in_day
                    line += f'\n{datetime.now().day - day + 1}  /  {new_users_in_day}'

                    text = (
                        f'Всего пользователей в боте: <b>{num_users}</b>'
                        f'\nАктивных за 24 часа: <b>{num_users_active_from_24hours}</b>'
                        f'\nАктивных за неделю: <b>{num_users_active_from_week}</b>'
                        f'\n\nЧисло месяца  /  новых пользователей{line}'
                        f'\nВсего в этом месяце: <b>{new_users_in_month}</b>'
                    )

            elif command == '/users_info':
                try:
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.append((f'Всего пользователей в боте: {num_users}',))
                    ws.append((f'Активных за 24 часа: {num_users_active_from_24hours}',))
                    ws.append((f'Активных за неделю: {num_users_active_from_week}',))
                    ws.append(('',))

                    ws.append(('Число месяца  /  новых пользователей',))
                    new_users_in_month = 0
                    for day in range(datetime.now().date().day, 0, -1):
                        new_users_in_day = await self.dbase.count_users(
                            register=True,
                            date=datetime.now().date()-timedelta(days=day - 1)
                        )
                        new_users_in_month += new_users_in_day
                        ws.append((f'{datetime.now().day - day + 1}  /  {new_users_in_day}',))
                    ws.append((f'Всего в этом месяце: {new_users_in_month}',))
                    ws.append(('',))

                    ws.append((
                        'Telegram_id', 'Name', 'Username', 'Дата регистрации',
                        'Дата последнего запроса', 'Текст последнего запроса',
                        'Всего запросов', 'Бан от пользователя', "Компания", "Роль",
                        "О компании", "О команде"
                    ))
                    for user in await self.dbase.select_all_contacts_users():
                        if tg_user_id := user.get("tg_user_id"):
                            dj_user: User = await (User.objects.filter(
                                tg_accounts__tg_user_id=tg_user_id).select_related(
                                "company").afirst())
                            username = user.get("tg_username")
                            ws.append((
                                tg_user_id,
                                user.get("tg_first_name"),
                                f'{f"@{username}" if username else ""}',
                                str(user.get("added_date").strftime('%d.%m.%Y %H:%M:%S')),
                                str(user.get("date_last_request").strftime('%d.%m.%Y %H:%M:%S')),
                                user.get("text_last_request"),
                                user.get("num_requests"),
                                "бан" if user.get("ban_from_user") else "нет",
                                dj_user.company.name if dj_user and dj_user.company else "",
                                dj_user.role_in_company if dj_user and dj_user.company else "",
                                dj_user.company.about_company if dj_user and dj_user.company else "",
                                dj_user.company.about_team if dj_user and dj_user.company else "",

                            ))
                    wb.save('users_info.xlsx')
                    text = open('users_info.xlsx', 'rb')
                    type_result = 'document'
                except Exception as exc:
                    self.logger.error(exc)
        return text, next_state, type_result

    async def in_password(self, update: Message, current_state: FSMAdminStates) -> Tuple:
        """Запрос пароля перед рассылкой"""
        password: str = await self.dbase.select_password(user_id=update.from_user.id)

        text = None
        next_state = None

        if update.text != password:
            text = f'Пароль не верный'
            next_state = None

        else:
            if current_state == 'FSMAdminStates:password_mailing':
                text = f'Введите сообщение для рассылки:'
                next_state = FSMAdminStates.mailing

        return text, next_state

    async def mailing(self, update: Message, only_admins: bool = False) -> Tuple:
        """Рассылка"""

        dict_errors = {}
        num_send = 0

        if only_admins:
            id_users = tuple(set(self.admins + self.tech_admins))
        else:
            # рассылка по всем, нужна для обновления данных
            # id_users: tuple = self.dbase.get_all_users(id_only=True)
            # рассылка по тем кто не забанил бота
            id_users: tuple = await self.dbase.get_all_users(id_only=True, not_ban=True)

        start_mailing = datetime.now()

        for i_list_part in [list_part for list_part in await self.split_users_list(id_users)]:
            data = [self.fast_send_message(
                update=update, user_id=user_id) for user_id in i_list_part]
            list_result = await asyncio.gather(*data)

            for result in list_result:
                if result[0]:
                    num_send += 1
                else:
                    error = result[1]
                    dict_errors[error] = dict_errors.get(error)+1 if dict_errors.get(error) else 1

            await asyncio.sleep(1)

        time_mailing = datetime.strftime(datetime.utcfromtimestamp(
            timedelta.total_seconds(datetime.now() - start_mailing)), '%H:%M:%S')

        await admins_send_message.func_admins_message(
            update=update,
            message='&#9888 <b>Ошибки рассылки:</b>\n'
                    f'<b>Errors:</b> {dict_errors or "нет"}\n'
                    f'<b>Отправлено:</b> {num_send} из {len(id_users)}\n'
                    f'<b>Время рассылки:</b> {time_mailing}'
        )

        text = f'<b>Отправлено:</b> {num_send} из {len(id_users)}'
        next_state = None
        if DEBUG:
            self.logger.debug(self.sign + f'OK -> send {num_send} out of {len(id_users)} users')

        return text, next_state

    async def fast_send_message(self, update: Message, user_id) -> Tuple:
        """Быстрая рассылка"""
        try:
            if update.content_type in ('photo',):
                await self.bot.send_photo(
                    chat_id=user_id, photo=update.photo[0].file_id, caption=update.caption)
            elif update.content_type in ('sticker',):
                await self.bot.send_sticker(
                    chat_id=user_id, sticker=update.sticker.file_id)
            elif update.content_type in ('document',):
                await self.bot.send_document(
                    chat_id=user_id, document=update.document.file_id, caption=update.caption)
            elif update.content_type in ('video',):
                await self.bot.send_video(
                    chat_id=user_id, video=update.video.file_id, caption=update.caption)
            elif update.content_type in ('video_note',):
                await self.bot.send_video_note(
                    chat_id=user_id, video_note=update.video_note.file_id)
            elif update.content_type in ('audio',):
                await self.bot.send_audio(
                    chat_id=user_id, audio=update.audio.file_id, caption=update.caption)
            elif update.content_type in ('voice',):
                await self.bot.send_voice(chat_id=user_id, voice=update.voice.file_id)
            else:
                await self.bot.send_message(chat_id=user_id, text=f'{update.text}')
        # удалено в aiogram==3.1.1
        except (BotBlocked, UserDeactivated, ChatNotFound) as error:
        # except TelegramAPIError as error:
            error = error.__repr__()
            # dict_errors[error] = dict_errors.get(error) + 1 if dict_errors.get(error) else 1
            if DEBUG:
                self.logger.error(self.sign + f'BAD -> not send to user {user_id} error: {error}')
            await self.dbase.update_ban_from_user(update=update, ban_from_user=True)
            return False, error

        except Exception as error:
            error = error.__repr__()
            # dict_errors[error] = dict_errors.get(error) + 1 if dict_errors.get(error) else 1
            if DEBUG:
                self.logger.error(self.sign + f'BAD -> not send to user {user_id} error: {error}')
            return False, error

        # Чтобы ускорить рассылку закомментировать код ниже
        else:
            await self.dbase.update_ban_from_user(update=update, ban_from_user=False)

        return True, None

    async def block_unblock_user(self, user_id, block: bool = False) -> Tuple:
        """Блокировка/разблокировка пользователя"""
        text, next_state = None, 'not_reset'
        if user_id.isdigit():

            if result := await self.dbase.update_user_access(user_id=user_id, block=block):

                text = (
                    f'<b>Пользователь:</b> {user_id}\n'
                    f'{"<b>Контакт:</b> https://t.me/" + result[1] if result[1] else ""}\n'
                    f'<b>{"ЗАБЛОКИРОВАН" if block else "РАЗБЛОКИРОВАН"}</b>'
                )

                next_state = None

            else:
                text = f'Пользователь: <b>{user_id}</b> в базе не зарегистрирован'
        else:
            text = 'Введены некорректные данные'
        return text, next_state

    async def change_user_balance(self, data: str) -> Tuple:
        """Изменяет денежный баланс пользователя"""
        text, next_state = None, 'not_reset'

        if len(data) == 2 and data[0].isdigit() and data[1].startswith(('+', '-', '0')):
            user_id = data[0]
            up_balance = data[1][1:] if data[1].startswith('+') else None
            down_balance = data[1][1:] if data[1].startswith('-') else None
            zero_balance = True if data[1] == '0' else None

            if result := await self.dbase.update_user_balance(
                    user_id=user_id,
                    up_balance=up_balance,
                    down_balance=down_balance,
                    zero_balance=zero_balance
            ):

                if not result[0] and result[1] == 'bad data':
                    text = (
                        f'Ошибка обновления баланса, возможно введены некорректные данные, '
                        f'баланс пользователя: <b>{user_id}</b> не изменён'
                    )
                else:
                    text = (
                        f'Баланс пользователя\n<b>id:</b> {user_id}\n'
                        f'{"<b>Контакт:</b> https://t.me/" + result[2] if result[2] else ""}\n'
                        f'ОБНОВЛЕН, новый баланс: <b>{result[1]}</b>'
                    )
                    next_state = None
            else:
                text = f'Пользователь: <b>{user_id}</b> в базе не зарегистрирован'
        else:
            text = 'Введены некорректные данные'

        return text, next_state

    async def change_user_requests_balance(self, data: str) -> Tuple:
        """Изменяет баланс количества доступных запросов пользователя"""
        text, next_state = None, 'not_reset'

        if len(data) == 2 and data[0].isdigit() and data[1].startswith(('+', '-', '0')):
            user_id = data[0]
            up_balance = data[1][1:] if data[1].startswith('+') else None
            down_balance = data[1][1:] if data[1].startswith('-') else None
            zero_balance = True if data[1] == '0' else None

            if result := await self.dbase.update_user_balance_requests(
                    user_id=user_id,
                    up_balance=up_balance,
                    down_balance=down_balance,
                    zero_balance=zero_balance
            ):

                if not result[0] and result[1] == 'bad data':
                    text = (
                        f'Ошибка обновления баланса запросов, '
                        f'возможно введены некорректные данные, '
                        f'баланс запросов пользователя: <b>{user_id}</b> не изменён'
                    )
                else:
                    text = (
                        f'Баланс запросов пользователя\n<b>id:</b> {user_id}\n'
                        f'{"<b>Контакт:</b> https://t.me/" + result[2] if result[2] else ""}\n'
                        f'ОБНОВЛЕН, новый баланс запросов: <b>{result[1]}</b>'
                    )
                    next_state = None
            else:
                text = f'Пользователь: <b>{user_id}</b> в базе не зарегистрирован'
        else:
            text = 'Введены некорректные данные'

        return text, next_state

    async def unload_payments_data_user(self, user_id) -> Tuple:
        """Возвращает дескриптор exel файла со сводной таблицей и технические данные"""
        result, type_result, next_state = (
            f'Нет данных об оплатах пользователя id: {user_id}', None, None)
        if not str(user_id).isdigit():
            payments_data = None
        else:
            payments_data = await self.dbase.select_all_payment_orders_user(user_id=user_id)

        if payments_data:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append((f'Таблица данных по оплатам от пользователя - id: {user_id}',))
            ws.append(('',))

            ws.append((
                'order_id', 'payment_status', 'user_id', 'payment_link', 'payment_link_data',
                'notification_data', 'payment_system', 'order_id_payment_system'
            ))
            for payment_order in payments_data:
                ws.append((
                    str(payment_order.id),
                    str(payment_order.payment_status),
                    str(payment_order.user_id),
                    str(payment_order.payment_link),
                    str(payment_order.payment_link_data),
                    str(payment_order.notification_data),
                    str(payment_order.payment_system),
                    str(payment_order.order_id_payment_system)
                ))

            wb.save('unload_payment_data_user.xlsx')
            result = open('unload_payment_data_user.xlsx', 'rb')
            type_result = 'document'
        return result, type_result, next_state

    @staticmethod
    async def get_obj_size(obj) -> int:
        """Возвращает размер объекта в байтах"""
        import gc
        import sys
        marked = {id(obj)}
        obj_q = [obj]
        sz = 0
        while obj_q:
            cur_obj = obj_q.pop(0)
            sz += sys.getsizeof(cur_obj)
            all_refr = ((id(o), o) for o in gc.get_referents(cur_obj))
            new_refr = list(filter(lambda o: o[0] not in marked, all_refr))
            if len(new_refr) > 0:
                refr_id, refr = zip(*new_refr)
                obj_q.extend(refr)
                marked.update(refr_id)
        return sz

    @classmethod
    async def load_stat(cls) -> str:
        """Отчет о нагрузке на систему"""
        gb = 1073741824
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        disc = psutil.disk_usage('/')
        vals = {
            1: (1, 'byte'),
            2: (1, 'byte'),
            3: (1, 'byte'),
            4: (1024, 'Kb'),
            5: (1024, 'Kb'),
            6: (1024, 'Kb'),
            7: (1048576, 'Mb'),
            8: (1048576, 'Mb'),
            9: (1048576, 'Mb'),
            10: (1073741824, 'Gb'),
            11: (1073741824, 'Gb')
        }
        gen_coll = await cls.get_obj_size(Base.general_collection)
        num = len(str(gen_coll))
        result = (
            '&#9888 <b><i>Нагрузка системы</i></b>:\n'
            f'<b>Нагрузка CPU</b>:    {psutil.cpu_percent(interval=1)} %\n'
            f'<b>Нагрузка RAM</b>:    {virtual_memory.percent} %\n'
            f'<b>Нагрузка SWAP</b>:    {swap_memory.percent} %\n'
            f'<b>Заполнение HDD</b>:    {disc.percent} %\n\n'
            f'<b>Физических CPU</b>:    {psutil.cpu_count(logical=False)} шт\n'
            f'<b>Логических CPU</b>:    {psutil.cpu_count()} шт\n'
            f'<b>Размер RAM</b>:    {round(virtual_memory.total / gb, 2)} Gb\n'
            f'<b>Размер SWAP</b>:    {round(swap_memory.total / gb, 2)} Gb\n'
            f'<b>Размер HDD</b>:    {round(disc.total / gb, 2)} Gb\n'
            f'<b>General collection</b>:    '
            f'{round(gen_coll / vals.get(num)[0], 2)} {vals.get(num)[1]}\n'
        )
        return result

    async def check_proxies(self) -> str:
        """Проверяет доступность прокси серверов"""
        data = await self.requests_manager.check_all_proxies()
        working_proxies = [val for val in data.values() if val is True]
        failed_proxies = [val for val in data.values() if val is False]
        result = (
            '&#9888 <b><i>Проверка прокси серверов</i></b>:\n'
            f'<b>Всего прокси</b>:    {len(data)} \n'
            f'<b>Работают</b>:    {len(working_proxies)}\n'
            f'<b>Не работают</b>:    {len(failed_proxies)}\n\n'
        )

        if failed_proxies and len(failed_proxies) <= 10:
            result += f'<b>Cписок неработающих прокси</b>:\n'
            for key, value in data.items():
                if value is False:
                    result += f'{key}\n'

        return result
