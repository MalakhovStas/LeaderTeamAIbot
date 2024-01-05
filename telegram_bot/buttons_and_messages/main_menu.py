from typing import Optional, List

from .base_classes import BaseButton
from .openai_menu import QuestionOpenAI
from .personal_cabinet import PersonalCabinet
from .company_menu import CompanyMenu
from ..config import SUPPORT, FACE_BOT, DEFAULT_GREETING, CONTACT_MANAGER


class AboutBot(BaseButton):
    """Класс описывающий кнопку - О боте"""

    def _set_name(self) -> str:
        return 'ℹ \t О боте'

    def _set_reply_text(self) -> str:
        return DEFAULT_GREETING


class SupportButton(BaseButton):
    """Класс описывающий кнопку - Поддержка"""

    def _set_name(self) -> str:
        return '🆘 \t Поддержка'

    def _set_reply_text(self) -> Optional[str]:
        return None

    def _set_url(self) -> Optional[str]:
        return SUPPORT


class ContactManagerButton(BaseButton):
    """Класс описывающий кнопку - Связь с менеджером"""

    def _set_name(self) -> str:
        return '🧑‍💻 \t Связаться с менеджером'

    def _set_reply_text(self) -> Optional[str]:
        return None

    def _set_url(self) -> Optional[str]:
        return CONTACT_MANAGER


class MainMenu(BaseButton):
    """Класс описывающий кнопку - Главное меню"""

    def _set_name(self) -> str:
        return 'ℹ \t Главное меню'  # 📒

    def _set_reply_text(self) -> str:
        return self.default_choice_menu

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [
            PersonalCabinet(parent_name=self.class_name),
            CompanyMenu(parent_name=self.class_name),
            QuestionOpenAI(parent_name=self.class_name),
            ContactManagerButton(parent_name=self.class_name),
            AboutBot(parent_name=self.class_name),
            SupportButton(parent_name=self.class_name),
        ]
