"""Модуль формирования меню - личный кабинет"""
from typing import List, Optional, Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from core.utils.i18n import I18N
from utils import utils
from .base_classes import Utils, BaseButton, BaseMessage, GoToBack
from .before_greeting_script import PersonalDataProcessingAgreement
from ..config import SYMS
from ..utils.states import FSMPersonalCabinetStates


class MessageGetNewFIO(BaseMessage, Utils):
    """Сообщение при изменении ФИО"""

    def _set_state_or_key(self) -> str:
        return 'FSMPersonalCabinetStates:change_fio'

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить Имя/Фамилию',
            en='Failed to change Name/Surname',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            name, surname, patronymic = utils.get_fullname(update.text)
            if name:
                user.name = name
                user.surname = surname
                user.patronymic = patronymic
                await user.asave()

                reply_text = I18N(
                    ru='Звучит очень красиво',
                    en='Sounds very nice',
                    common_right=SYMS.smile
                )
                next_state = self.reset_state
            else:
                reply_text = I18N(
                    ru='Ошибка изменения данных\n<b>Имя не может быть пустым',
                    en='Data modification error\n<b>Name cannot be empty',
                    common_left=SYMS.warning,
                )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangeFIO(BaseButton, Utils):
    """Кнопка изменить ФИО"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Изменить Имя/Фамилию', en='Change Name/Surname', common_left=SYMS.writing)

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Напишите мне, как вас зовут, в порядке -  Имя Фамилия',
            en='Write to me what your name is, in order - Name Surname',
            common_left=SYMS.bot_face
        )

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

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить Telegram-ник',
            en='Failed to change Telegram nickname',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            user.username = update.text[:256].split()[0]
            await user.asave()

            reply_text = I18N(
                ru='Спасибо, я запомню',
                en="Thank you, I'll remember",
                common_right=SYMS.smile
            )
            next_state = self.reset_state
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangeUsername(BaseButton, Utils):
    """Кнопка Изменить Telegram-ник"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Изменить Telegram-ник', en='Change Telegram nickname', common_left=SYMS.man
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите ваш новый ник для Telegram',
            en='Enter your new nickname for Telegram',
            common_left=SYMS.bot_face
        )

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

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить электронную почту',
            en='Failed to change email',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            if email := await utils.data_to_email(update.text):
                user.email = email
                await user.asave()

                reply_text = I18N(
                    ru='Зафиксировано',
                    en='Recorded',
                    common_right=SYMS.wink
                )
                next_state = self.reset_state

            else:
                reply_text = I18N(
                    ru='Ошибка изменения адреса электронной почты\nВведите адрес в формате',
                    en='Error changing email address\nEnter the address in the format',
                    common_left=SYMS.warning,
                    common_right=SYMS.email_format,
                    common_style='bold'
                )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangeEmail(BaseButton, Utils):
    """Кнопка изменить email"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Изменить электронную почту', en='Change email', common_left=SYMS.email)

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Напишите вашу новую электронную почту в формате mail@mail.com',
            en='Write your new email in the format mail@mail.com',
            common_left=SYMS.bot_face
        )

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

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить номер телефона',
            en='Failed to change phone number',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            if phone_number := await utils.data_to_phone(update.text):
                user.phone_number = phone_number
                await user.asave()
                reply_text = I18N(
                    ru='Класс. Обещаю не названивать в 4 утра',
                    en='Class. I promise not to call at 4 am',
                    common_right=SYMS.laughter
                )
                next_state = self.reset_state
            else:
                reply_text = I18N(
                    ru='Ошибка изменения номера телефона\nВведите номер телефона в формате',
                    en='Error changing phone number\nEnter the phone number in the format',
                    common_left=SYMS.warning,
                    common_right=SYMS.phone_format,
                    common_style='bold'
                )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangePhoneNumber(BaseButton, Utils):
    """Кнопка изменить номер телефона"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Изменить номер телефона', en='Change phone number', common_left=SYMS.phone
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите ваш новый номер телефона в формате',
            en='Enter your new phone number in the format',
            common_left=SYMS.bot_face,
            common_right=' 79998887766',
            common_style='bold'
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMPersonalCabinetStates.change_phone_number

    def _set_messages(self) -> Dict:
        messages = [MessageGetNewPhoneNumber(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class ChangeLanguage(BaseButton, Utils):
    """Кнопка Изменить язык"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru=f'{SYMS.flag_ru}Изменить язык', en=f'{SYMS.flag_en}Change language')

    async def _set_answer_logic(self, update: CallbackQuery, state: Optional[FSMContext] = None):
        await I18N.switch_language(user=update.user)

        personal_cabinet = PersonalCabinet(new=False)
        self.children_buttons = personal_cabinet.children_buttons

        return await personal_cabinet._set_answer_logic(update, state)


class PersonalCabinet(BaseButton):
    """Класс описывающий кнопку - Обо мне"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Обо мне', en='About me', common_left=f'{SYMS.handshake}{SYMS.tab}')

    def _set_next_state(self) -> str:
        return self.reset_state

    async def _set_answer_logic(self, update: CallbackQuery, state: Optional[FSMContext] = None):
        user = update.user
        reply_text = I18N(
            ru='То, что вы рассказали мне о себе ',
            en='What you told me about yourself ',
            style='bold',
            common_left=SYMS.bot_face,
            common_right=SYMS.smile + '\n\n',
        )
        reply_text += I18N(
            ru="Имя",
            en="Name",
            style='bold_italic',
            common_right=f": {user.name if user.name else ''}\n"
        )
        reply_text += I18N(
            ru="Фамилия",
            en="Surname",
            style='bold_italic',
            common_right=f": {user.surname if user.surname else ''}\n"
        )

        # if user.patronymic:
        #     reply_text += I18N(
        #         ru="Отчество",
        #         en="Patronymic",
        #         style='bold_italic',
        #         common_right=f": {user.patronymic if user.patronymic else ''}{SYMS.nl}"
        #     )

        if user.username:
            reply_text += I18N(
                ru="Telegram-ник",
                en="Telegram-nik",
                style='bold_italic',
                common_right=f": {user.username if user.username else ''}\n"
            )

        if user.email:
            reply_text += I18N(
                ru="Электронная почта",
                en="Email",
                style='bold_italic',
                common_right=f": {user.email if user.email else ''}\n"
            )

        if user.phone_number:
            reply_text += I18N(
                ru="Номер телефона",
                en="Phone number",
                style='bold_italic',
                common_right=f": {user.phone_number if user.phone_number else ''}\n"

            )
        if user.company:
            reply_text += I18N(
                ru="Компания",
                en="Company",
                style='bold_italic',
                common_right=f": {user.company.name if user.company else ''}\n"
            )

        reply_text += I18N(
            ru="Откорректируйте, если у вас что-то поменялось",
            en="Please correct if anything has changed",
            # style='bold',
            common_left='\n',
            common_right=SYMS.down

        )
        return reply_text, self.next_state

    def _set_children(self) -> List:
        return [
            ChangeFIO(parent_name=self.class_name),
            ChangeUsername(parent_name=self.class_name),
            ChangeEmail(parent_name=self.class_name),
            ChangePhoneNumber(parent_name=self.class_name),
            ChangeLanguage(parent_name=self.class_name),
            PersonalDataProcessingAgreement(parent_name=self.class_name),
        ]
