from typing import List

from .base_classes import BaseButton
from .company_menu import CompanyMenu
from .contacts_buttons import ContactManagerButton, SupportButton
from .greeting_script import StartGreetingButton
from .openai_menu import QuestionOpenAI
from .personal_cabinet import PersonalCabinet
from .seven_petals_script import SevenPetalsSurveyButton
from ..config import DEFAULT_GREETING


class AboutBot(BaseButton):
    """Класс описывающий кнопку - О боте"""

    def _set_name(self) -> str:
        return '🧑‍💻 \t Об ассистенте'

    def _set_reply_text(self) -> str:
        return DEFAULT_GREETING


class MainMenu(BaseButton):
    """Класс описывающий кнопку - Главное меню"""
    greeting_button_script = StartGreetingButton()

    def _set_name(self) -> str:
        return 'ℹ \t Главное меню'  # 📒

    def _set_reply_text(self) -> str:
        return self.default_choice_menu

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [
            # StartGreetingButton(parent_name=self.class_name),
            PersonalCabinet(parent_name=self.class_name),
            CompanyMenu(parent_name=self.class_name),
            # SevenPetalsSurveyButton(parent_name=self.class_name),
            QuestionOpenAI(parent_name=self.class_name),
            ContactManagerButton(parent_name=self.class_name),
            AboutBot(parent_name=self.class_name),
            SupportButton(parent_name=self.class_name),
        ]
