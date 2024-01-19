"""Модуль формирования меню - личный кабинет"""
from typing import List, Optional, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from users.models import User
from utils import utils
from .base_classes import Utils, BaseButton, BaseMessage, GoToBack
from ..config import FACE_BOT
from ..utils.states import FSMPersonalCabinetStates


class MessageGetNewFIO(BaseMessage, Utils):
    """Сообщение при изменении ФИО"""
    def _set_state_or_key(self) -> str:
        return 'FSMPersonalCabinetStates:change_fio'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>⚠ Не удалось изменить Имя/Фамилию</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            name, surname, patronymic = utils.get_fullname(update.text)
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            if name:
                user.name = name
                user.surname = surname
                user.patronymic = patronymic
                await user.asave()
                reply_text = "<b>Данные успешно изменены</b>"
                next_state = 'reset_state'
            else:
                reply_text = "⚠ Ошибка изменения данных\n<b>Имя не может быть пустым</b>"
        except Exception as exc:
            self.logger.error(exc)
        return reply_text, next_state


class ChangeFIO(BaseButton, Utils):
    """Кнопка изменить ФИО"""
    def _set_name(self) -> str:
        return '✍ Изменить Имя/Фамилию'  # 🔑 🔐 🗝

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + ('<b>Введите через пробел новые '
                           'имя и фамилию в указанном порядке:</b>')

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMPersonalCabinetStates.change_fio

    def _set_messages(self) -> Dict:
        messages = [MessageGetNewFIO(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageGetNewNickname(BaseMessage, Utils):
    """Сообщение при изменении username"""
    def _set_state_or_key(self) -> str:
        return 'FSMPersonalCabinetStates:change_username'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>⚠ Не удалось изменить Username</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            user.username = update.text[:256].split()[0]
            await user.asave()
            reply_text = "<b>Username успешно изменён</b>"
            next_state = 'reset_state'
        except Exception as exc:
            self.logger.error(exc)
        return reply_text, next_state


class ChangeUsername(BaseButton, Utils):
    """Кнопка изменить username"""
    def _set_name(self) -> str:
        return '👤 Изменить Username'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Введите новый Username</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMPersonalCabinetStates.change_username

    def _set_messages(self) -> Dict:
        messages = [MessageGetNewNickname(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageGetNewEmail(BaseMessage, Utils):
    """Сообщение при изменении email"""
    def _set_state_or_key(self) -> str:
        return 'FSMPersonalCabinetStates:change_email'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>⚠ Не удалось изменить электронную почту</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            if email := await utils.data_to_email(update.text):
                user.email = email
                await user.asave()
                reply_text = "<b>Адрес электронной почты  успешно изменён</b>"
                next_state = 'reset_state'
            else:
                reply_text = ("<b>⚠ Ошибка изменения адреса электронной почты\n"
                              "Введите Email в формате mail@mail.com</b>")
        except Exception as exc:
            self.logger.error(exc)
        return reply_text, next_state


class ChangeEmail(BaseButton, Utils):
    """Кнопка изменить email"""
    def _set_name(self) -> str:
        return '📧 Изменить Email'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Введите Email в формате mail@mail.com</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMPersonalCabinetStates.change_email

    def _set_messages(self) -> Dict:
        messages = [MessageGetNewEmail(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageGetNewPhoneNumber(BaseMessage, Utils):
    """Сообщение при изменении номера телефона"""
    def _set_state_or_key(self) -> str:
        return 'FSMPersonalCabinetStates:change_phone_number'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>⚠ Не удалось изменить номер телефона</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            if phone_number := await utils.data_to_phone(update.text):
                user.phone_number = phone_number
                await user.asave()
                reply_text = "<b>Номер телефона успешно изменён</b>"
                next_state = 'reset_state'
            else:
                reply_text = ("<b>⚠ Ошибка изменения номера телефона\n"
                              "Введите номер телефона в формате 79998887766</b>")
        except Exception as exc:
            self.logger.error(exc)
        return reply_text, next_state


class ChangePhoneNumber(BaseButton, Utils):
    """Кнопка изменить номер телефона"""
    def _set_name(self) -> str:
        return '☎ Изменить номер телефона'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Введите номер телефона в формате 79998887766</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMPersonalCabinetStates.change_phone_number

    def _set_messages(self) -> Dict:
        messages = [MessageGetNewPhoneNumber(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class PersonalCabinet(BaseButton):
    """Класс описывающий кнопку - Профиль"""

    def _set_name(self) -> str:
        return '⚙ \t Профиль'

    def _set_next_state(self) -> str:
        return 'reset_state'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user_id = update.from_user.id
        user = await User.objects.filter(
            tg_accounts__tg_user_id=user_id).select_related("company").afirst()
        reply_text = f"<b>{FACE_BOT}Информация о вашем профиле:</b>\n\n"
        reply_text += f"<b>Имя:</b> {user.name if user.name else ''}\n"
        reply_text += f"<b>Фамилия:</b> {user.surname if user.surname else ''}\n"
        # reply_text += f"<b>Отчество:</b> {user.patronymic if user.patronymic else ''}\n"
        reply_text += f"<b>Username:</b> {user.username if user.username else ''}\n"
        reply_text += f"<b>Email:</b> {user.email if user.email else ''}\n"
        reply_text += f"<b>Номер телефона:</b> {user.phone_number  if user.phone_number else ''}\n"
        reply_text += f"<b>Компания:</b> {user.company.name if user.company else ''}\n"
        return reply_text, self.next_state

    def _set_children(self) -> List:
        return [
            ChangeFIO(parent_name=self.class_name),
            ChangeUsername(parent_name=self.class_name),
            ChangeEmail(parent_name=self.class_name),
            ChangePhoneNumber(parent_name=self.class_name),
        ]
