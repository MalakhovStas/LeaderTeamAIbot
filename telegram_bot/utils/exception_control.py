"""Модуль декоратора для контроля исключений"""
import functools
from typing import Callable, Any, Optional, Union
from aiogram.dispatcher.handler import CancelHandler

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, Update
from aiogram.utils.exceptions import TelegramAPIError
from ..loader import logger, storage
from ..config import DEBUG


def exception_handler_wrapper(func: Callable) -> Callable:
    """
    Декоратор, контролирует выполнение кода в функции, в случае успешного выполнения возвращает
    результат выполнения функции, в случае исключения сбрасывает дальнейшую обработку сообщения
    от пользователя, его состояние и возвращает None. Также информирует администраторов об ошибке
    в процессе обработки запроса от пользователя.
    """

    @functools.wraps(func)
    async def wrapped_func(*args, **kwargs) -> Optional[Any]:
        try:
            result = await func(*args, **kwargs)
            return result

        except CancelHandler:
            raise CancelHandler()

        except BaseException as exc:
            try:
                arg = [arg for arg in args if isinstance(arg, (Message, CallbackQuery, Update))]
                if arg:
                    """ Первый неименованный аргумент любой обёрнутой
                    функции должен быть объектом одним из """
                    update: Union[Message, CallbackQuery, Update] = arg[0]

                    """ Проверка для middlewares """
                    if isinstance(update, Update):
                        if update.message:
                            update = update.message
                        elif update.callback_query:
                            update = update.callback_query

                else:
                    """ Если все аргументы именованные, должен быть аргумент
                    "update" -> объектом одним из """
                    update: Union[Message, CallbackQuery] = kwargs.get('update')
                if DEBUG:
                    logger.error(f'user_id: {update.from_user.id}, username: '
                                 f'{update.from_user.first_name} -> Module: {func.__module__} | '
                                 f'Func: {func.__name__} -> Exception: {exc.__class__.__name__} '
                                 f'-> Traceback: {exc}')

                if not exc.__class__ == TelegramAPIError:
                    """ Отправляет сообщение об ошибке подробное админам и информационное
                        пользователю если это не одно из исключений TelegramAPI """
                    from ..utils import admins_send_message
                    await admins_send_message.func_admins_message(update=update, exc=exc)

                    # text = f'&#9888 В моей программе произошла непредвиденная ошибка, ' \
                    #        f'попробуйте ещё раз, или обратитесь в поддержку @{SUPPORT}'
                    # await bot.send_message(chat_id=update.from_user.id, text=text)

                    state_user = FSMContext(
                        storage=storage, chat=update.from_user.id, user=update.from_user.id)
                    await state_user.reset_state()

                else:
                    """ Если это одно из исключений TelegramAPI ->
                    выводит информацию в консоль и лог файл """
                    if DEBUG:
                        logger.error(f'-> ERROR -> Exception: {exc.__class__.__name__} -> '
                                     f'Traceback: {exc} -> User_name: '
                                     f'{update.from_user.first_name} '
                                     f'User_id: {update.from_user.id}')
                return None
            except BaseException as exc:
                if DEBUG:
                    logger.critical(f'CRITICAL_ERROR(exception_control.py): {exc}')

    return wrapped_func
