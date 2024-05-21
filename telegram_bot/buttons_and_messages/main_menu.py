from typing import List, Dict, Optional, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from core.utils.i18n import I18N
from telegram_bot.utils.states import FSMUtilsStates
from .base_classes import Utils, BaseButton, BaseMessage
from .before_greeting_script import StartBeforeGreeting
from .company_menu import CompanyMenu
from .contacts_buttons import ContactManagerButton, SupportButton
from .openai_menu import QuestionOpenAI
from .personal_cabinet import PersonalCabinet
from .seven_petals_script import SevenPetalsSurveyButton
from ..config import DEFAULT_GREETING
from ..config import SYMS


class MessageGetFeedback(BaseMessage, Utils):
    """Сообщение для получения отзыва от пользователя"""

    def _set_state_or_key(self) -> str:
        return 'FSMUtilsStates:get_feedback'

    def _set_next_state(self) -> Optional[str]:
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Благодарим за ваш отзыв, ответим ближайшее время',
            en='Thank you for your feedback, we will respond as soon as possible',
            common_left=SYMS.bot_face
        )

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        from core.models.feedbacks_model import Feedback
        try:
            if update.text:
                await Feedback.objects.acreate(user=update.user, feedback=update.text)
        except Exception as exc:
            self.log(message=exc, level='error')
        return self.reply_text, self.reset_state


class FeedbacksAndSuggestions(BaseButton):
    """Класс описывающий кнопку - Отзывы и предложения"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Отзывы и предложения',
            en='Feedback and suggestions',
            common_left=SYMS.book
        )

    def _set_next_state(self) -> Optional[str]:
        return FSMUtilsStates.get_feedback

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Отправьте ваш отзыв или предложение в ответном сообщении',
            en='Send your feedback or suggestion in reply message',
            common_left=SYMS.bot_face
        )

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message
                for message in [MessageGetFeedback(parent_name=self.class_name)]}


class AboutBot(BaseButton):
    """Класс описывающий кнопку - О боте"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Об ассистенте', en='About assistant', common_left=SYMS.bot_face)

    def _set_reply_text(self) -> Union[str, I18N]:
        return DEFAULT_GREETING


class MainMenu(BaseButton):
    """Класс описывающий кнопку - Главное меню"""
    start_before_greeting = StartBeforeGreeting()

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Главное меню', en='Main menu', common_left=SYMS.main_menu)

    def _set_reply_text(self) -> str:
        return self.default_choice_menu

    def _set_next_state(self) -> str:
        return self.reset_state

    def _set_children(self) -> List:
        return [
            # StartBeforeGreeting(parent_name=self.class_name),
            PersonalCabinet(parent_name=self.class_name),
            CompanyMenu(parent_name=self.class_name),
            SevenPetalsSurveyButton(parent_name=self.class_name),
            QuestionOpenAI(parent_name=self.class_name),
            ContactManagerButton(parent_name=self.class_name),
            FeedbacksAndSuggestions(parent_name=self.class_name),
            AboutBot(parent_name=self.class_name),
            SupportButton(parent_name=self.class_name),
        ]
