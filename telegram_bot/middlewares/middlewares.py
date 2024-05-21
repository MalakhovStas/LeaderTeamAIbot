"""Модуль предварительной и постобработки входящих сообщений"""
from typing import Dict, Optional, List

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update, ReplyKeyboardRemove
from django.conf import settings

from ..config import (
    DEFAULT_PROJECT_IN_DEV_MESSAGE
)
from ..loader import bot, security, dbase, Base, storage
from ..utils import exception_control, states
from users.models import User


class AccessControlMiddleware(BaseMiddleware):
    """Класс предварительной обработки входящих сообщений для защиты от
    нежелательной нагрузки и постобработки"""
    dbase = dbase
    bot = bot
    security = security

    def __init__(self) -> None:
        super().__init__()
        self.sign = self.__class__.__name__ + ': '

    @exception_control.exception_handler_wrapper
    async def on_pre_process_update(self, update: Update, update_data: Dict) -> None:
        command = None
        if update.message:
            command = update.message.get_command()

        update = update.message if update.message else update.callback_query
        state = FSMContext(storage=storage, chat=update.from_user.id, user=update.from_user.id)

        # print(update)
        # print(update.message.reply_markup.values.get('inline_keyboard')[0][0].text[-7:])
        # print(Base.general_collection)

        if settings.ADMINS_ACCESS_ONLY and update.from_user.id not in map(
                int, settings.TECH_ADMINS):
            await bot.send_message(
                chat_id=update.from_user.id,
                text=DEFAULT_PROJECT_IN_DEV_MESSAGE,
                reply_markup=ReplyKeyboardRemove()
            )
            raise CancelHandler()

        # TODO выяснить доступ к боту открыт или только по приглашению
        # варианты:
        # если Userа нет предлагаем войти по логину/паролю или создать новый аккаунт==User
        # ещё подумать


        # user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
        # if not user:
        #     if command == '/start' and len((command_list := update.text.split())) >= 2:
        #         code = command_list[1]
        #         if new_user := await User.objects.filter(code_tg_register_link=code).afirst():
        #
        #         # if new_user := await TelegramAccount.objects.filter(
        #         #             code_tg_register_link=code).afirst():
        #             new_user.tg_user_id = update.from_user.id
        #             new_user.first_name = update.from_user.first_name
        #             new_user.tg_username = update.from_user.username
        #             await new_user.asave()
        #         else:
        #             raise CancelHandler()
        #     else:
        #         raise CancelHandler()

        user_data = self.manager.storage.data.get(str(update.from_user.id))
        if isinstance(update, CallbackQuery):
            await self.bot.answer_callback_query(callback_query_id=update.id)

        user_status = await self.security.check_user(update, user_data)  # block|allowed|new_user
        if user_status == "block":
            raise CancelHandler()
        elif user_status == "new_user":
            await state.set_state(state=states.FSMBeforeGreetingScriptStates.start_before_greeting)
            await state.update_data(data={'new_user': True})

        text_last_request = "Message: " + str(update.text) if isinstance(
            update, Message) else "Callback: " + str(update.data)

        await self.dbase.update_last_request_data(
            update=update, text_last_request=text_last_request)

        if settings.FLOOD_CONTROL:
            control = await self.security.flood_control(update)
            if control in ['block', 'bad', 'blocked']:
                if control != 'blocked':
                    text = {'block': f'&#129302 Доступ ограничен на '
                                     f'{settings.FLOOD_CONTROL_STOP_TIME} секунд',
                            'bad': '&#129302 Не так быстро пожалуйста'}
                    await bot.send_message(chat_id=update.from_user.id, text=text[control])
                raise CancelHandler()

        # Добавляет экземпляр модели User к Message или CallbackQuery
        update.user = await User.objects.filter(
            tg_accounts__tg_user_id=update.from_user.id
        ).select_related("company").prefetch_related("seven_petals_user").afirst()

        # Если не подписано соглашение о, обработке персональных данных
        if not user_status == "new_user" and not update.user.personal_data_processing_agreement:
            await state.set_state(
                state=states.FSMBeforeGreetingScriptStates.personal_data_processing_agreement
            )

        from .. import handlers

    @exception_control.exception_handler_wrapper
    async def on_process_update(self, update: Update, update_data: Dict) -> Optional[Dict]:
        pass

    @exception_control.exception_handler_wrapper
    async def on_post_process_update(self, update: Update, post: List, update_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_pre_process_message(self, message: Message, message_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_process_message(self, message: Message, message_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_post_process_message(
            self, message: Message, post: List, message_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_pre_process_callback_query(
            self, call: CallbackQuery, callback_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_process_callback_query(self, call: CallbackQuery, callback_data: Dict) -> None:
        pass

    @exception_control.exception_handler_wrapper
    async def on_post_process_callback_query(
            self, call: CallbackQuery, post: List, callback_data: Dict) -> None:
        data = callback_data.get('state')
        if not call.data in ['UpdateData']:  #, 'GoToBack']:
            await data.update_data(previous_button=call.data)
            await Base.button_search_and_action_any_collections(
                user_id=call.from_user.id, action='add',
                button_name='previous_button', instance_button=call.data, updates_data=True)
