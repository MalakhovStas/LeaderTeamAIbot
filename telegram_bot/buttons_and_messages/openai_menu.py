import random
from typing import List, Tuple, Union, Optional, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from .base_classes import BaseButton, BaseMessage
from ..config import FACE_BOT, DEFAULT_FEED_ANSWER
from ..utils.states import FSMMainMenuStates
from users.models import User
from .contacts_buttons import ContactManagerButton


class RegenerateAIResponse(BaseButton):

    def _set_name(self) -> str:
        return '🔁 \t Предложи другой вариант'

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Извините, произошла ошибка, попробуйте немного позже'

    def _set_children(self) -> List:
        return [
            # self, SubmitForRevisionTaskQuestionOpenAI(new=False),
            CreateNewTaskForQuestionOpenAI(new=False),
            ContactManagerButton(new=False)
        ]

    async def _set_answer_logic(self, update: CallbackQuery,
                                state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        user_id = update.from_user.id
        reply_text = self.default_i_generate_text
        wait_msg = await self.bot.send_message(chat_id=user_id, text=self.default_generate_answer)

        if ai_messages_data := await self.button_search_and_action_any_collections(
                user_id=user_id, action='get', button_name='ai_messages_data', updates_data=True):

            # выкидывает последнюю генерацию
            ai_messages_data.pop(-1)
            # получает задание - prompt
            task_to_generate_ai = ai_messages_data.pop(-1).get('content')

            ai_answer = await self.ai.some_question(
                prompt=task_to_generate_ai,
                messages_data=ai_messages_data,
                user_id=user_id,
                update=update
            )
        else:
            ai_answer = DEFAULT_FEED_ANSWER

        if ai_answer != DEFAULT_FEED_ANSWER:
            reply_text = reply_text + ai_answer + ':ai:some_question'
        else:
            self.children_buttons = []
            reply_text = self.reply_text

        await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)

        return reply_text, self.next_state


class CreateNewTaskForQuestionOpenAI(BaseButton):
    """Кнопка старта нового задания"""

    def _set_name(self) -> str:
        return '📝 \t Обсудить другую тему'

    async def _set_answer_logic(
            self, update, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        # удаляет сохранённый контекст при ошибке
        await self.button_search_and_action_any_collections(
            user_id=update.from_user.id, action='pop',
            button_name='ai_messages_data',
            updates_data=True
        )
        logic_button = QuestionOpenAI(new=False)
        self.children_buttons = logic_button.children_buttons
        return await logic_button._set_answer_logic(update, state)


class MessageOnceForQuestionOpenAIButton(BaseMessage):
    """Формирует ответ на вопрос заданный OpenAI"""

    def _set_state_or_key(self) -> str:
        return 'FSMMainMenuStates:question_openai'

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Извините, произошла ошибка, попробуйте немного позже'

    def _set_next_state(self) -> str:
        return FSMMainMenuStates.question_openai

    def _set_children(self) -> List:
        return [
            RegenerateAIResponse(parent_name=self.class_name, parent_button=self),
            CreateNewTaskForQuestionOpenAI(parent_name=self.class_name, parent_button=self),
            ContactManagerButton(new=False)
        ]

    async def _set_answer_logic(
            self, update: Message, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        self.children_buttons = [
            RegenerateAIResponse(new=False),
            CreateNewTaskForQuestionOpenAI(new=False),
            ContactManagerButton(new=False)
        ]
        reply_text = self.default_i_generate_text
        user_id = update.from_user.id
        task_to_generate_ai = update.text.strip()
        wait_msg = await self.bot.send_message(chat_id=user_id, text=self.default_generate_answer)

        # возвращает сохраненный контекст
        ai_messages_data = await self.button_search_and_action_any_collections(
            user_id=user_id, action='get', button_name='ai_messages_data', updates_data=True)

        if not ai_messages_data:
            # добавляет к основному контексту
            ai_messages_data = await self.button_search_and_action_any_collections(
                user_id=user_id, action='add', button_name='ai_messages_data',
                instance_button=list(), updates_data=True)

        ai_answer = await self.ai.some_question(
            prompt=task_to_generate_ai,
            messages_data=ai_messages_data,
            user_id=user_id,
            update=update
        )

        if ai_answer != DEFAULT_FEED_ANSWER:
            reply_text = reply_text + ai_answer + ':ai:some_question'

        else:
            # удаляет сохранённый контекст при ошибке
            await self.button_search_and_action_any_collections(
                user_id=user_id, action='pop', button_name='ai_messages_data', updates_data=True)
            self.children_buttons = []
            reply_text = self.reply_text

        await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)

        user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
        user.ai_dialog += (f'\n\n🙋\t\t{task_to_generate_ai}'
                           f'\n\n{reply_text.rstrip(":ai:some_question")}')
        await user.asave()
        return reply_text, self.next_state


class QuestionOpenAI(BaseButton):
    """Класс описывающий кнопку - Задать вопрос OpenAI"""

    def _set_name(self) -> str:
        return '🙋 \t Задать вопрос ассистенту'  # ✍

    def _set_next_state(self) -> str:
        return FSMMainMenuStates.question_openai

    def _set_reply_text(self) -> str:
        return FACE_BOT + 'Извините, произошла ошибка, попробуйте немного позже'

    async def _set_answer_logic(
            self, update: Message, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        reply_text, next_state = self.reply_text, self.next_state
        user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
        if not user.ai_dialog:
            reply_text = (
                "Напишите ваш запрос. С чем у вас возникают проблемы? Где не хватает "
                "идей или фокуса? Хотите описать ключевые зоны роста? Без проблем! "
                "Главное начать! Старайтесь разделять большие запросы на небольшие "
                "конкретные части - тогда я буду максимально полезен для вас. Не "
                "переживайте, первые ответы могут приходить с небольшой задержкой, "
                "но я учусь быть побыстрее.")
        else:
            ai_greetings_list = [
                "<b>Что Вам интересно в этот раз?</b>",
                "<b>Ответ на какой вопрос вы хотите найти?</b>",
                "<b>Задавайте вопрос, с радостью помогу найти ответ</b>",
            ]
            reply_text = random.choice(ai_greetings_list)
        return reply_text, next_state

    def _set_messages(self) -> Dict:
        message = MessageOnceForQuestionOpenAIButton(parent_name=self.class_name)
        return {message.state_or_key: message}

    def _set_children(self) -> List:
        return [ContactManagerButton(new=False)]
