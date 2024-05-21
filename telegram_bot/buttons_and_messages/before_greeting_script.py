"""Модуль формирования сценаярия первого знакомства с новым пользователем"""
from typing import Optional, Union, List

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from core.utils.i18n import I18N
from .base_classes import BaseButton
from .greeting_script import StartGreetingButton
from ..config import SYMS, PERSONAL_DATA_PROCESSING_AGREEMENT
from ..utils.states import FSMBeforeGreetingScriptStates


class YesButton(BaseButton):
    """Класс описывающий кнопку - 'Да/Yes'"""
    start_greeting_button = StartGreetingButton()

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Да',
            en='Yes',
        )

    def _set_next_state(self) -> Optional[str]:
        return self.reset_state

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        user.personal_data_processing_agreement = True
        await user.asave()

        if (current_data := await state.get_data()) and current_data.get('new_user'):
            return self.start_greeting_button.reply_text, self.start_greeting_button.next_state
        else:
            from ..buttons_and_messages.main_menu import MainMenu
            main_menu = MainMenu(new=False)
            self.children_buttons = main_menu.children_buttons
            return main_menu.reply_text, main_menu.next_state


class NoButton(BaseButton):
    """Класс описывающий кнопку - 'Нет/No'"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Нет',
            en='No',
        )

    def _set_next_state(self) -> Optional[str]:
        return FSMBeforeGreetingScriptStates.personal_data_processing_agreement

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        user.personal_data_processing_agreement = False
        await user.asave()

        pdpa = PersonalDataProcessingAgreement(new=False)
        return pdpa.reply_text, self.next_state

    def _set_children(self) -> List:
        return [
            YesButton(new=False),
            self,
        ]


class PersonalDataProcessingAgreement(BaseButton):
    """Класс описывающий кнопку - PersonalDataProcessingAgreement кнопка не отображается"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Соглашение на обработку персональных данных',
            en='Personal data processing agreement'
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return PERSONAL_DATA_PROCESSING_AGREEMENT

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        current_state = await state.get_state()
        if current_state == 'FSMGreetingScriptStates:personal_data_processing_agreement':
            next_state = FSMBeforeGreetingScriptStates.personal_data_processing_agreement
        else:
            next_state = self.reset_state
        return self.reply_text, next_state

    def _set_children(self) -> List:
        return [
            YesButton(parent_name=self.class_name),
            NoButton(parent_name=self.class_name),
        ]


class RusButton(BaseButton):
    """Класс описывающий кнопку - 'RUS'"""
    sgb = PersonalDataProcessingAgreement(new=False)

    def _set_name(self) -> Union[str, I18N]:
        return f'{SYMS.flag_ru} RUS'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        user.language = 'ru'
        await user.asave()

        return self.sgb.reply_text, self.sgb.next_state

    def _set_children(self) -> List:
        return self.sgb.children_buttons


class EngButton(BaseButton):
    """Класс описывающий кнопку - 'ENG'"""
    sgb = PersonalDataProcessingAgreement(new=False)

    def _set_name(self) -> Union[str, I18N]:
        return f'{SYMS.flag_en} ENG'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        user.language = 'en'
        await user.asave()

        return self.sgb.reply_text, self.sgb.next_state

    def _set_children(self) -> List:
        return self.sgb.children_buttons


class StartBeforeGreeting(BaseButton):
    """Класс описывающий кнопку - FirstSelectLanguage кнопка не отображается"""
    PersonalDataProcessingAgreement()

    def _set_reply_text(self) -> Union[str, I18N]:
        return 'Выберите язык / Select language'

    def _set_next_state(self) -> Optional[str]:
        return FSMBeforeGreetingScriptStates.first_select_language

    def _set_children(self) -> List:
        return [
            RusButton(parent_name=self.class_name),
            EngButton(parent_name=self.class_name),
        ]
