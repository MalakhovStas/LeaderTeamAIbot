from typing import Optional

from .base_classes import BaseButton
from ..config import SUPPORT, CONTACT_MANAGER


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
