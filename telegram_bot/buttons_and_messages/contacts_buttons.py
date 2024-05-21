from typing import Optional, Union

from django.conf import settings

from core.utils.i18n import I18N
from .base_classes import BaseButton
from ..config import SYMS


class SupportButton(BaseButton):
    """Класс описывающий кнопку - Поддержка"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Техподдержка',
            en='Technical support',
            common_left=SYMS.tech_support,
        )

    def _set_reply_text(self) -> Optional[str]:
        return None

    def _set_url(self) -> Optional[str]:
        return settings.SUPPORT


class ContactManagerButton(BaseButton):
    """Класс описывающий кнопку - Связь с менеджером"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Связаться с менеджером',
            en='Contact the manager',
            common_left=SYMS.manager,
        )

    def _set_reply_text(self) -> Optional[str]:
        return None

    def _set_url(self) -> Optional[str]:
        return settings.CONTACT_MANAGER
