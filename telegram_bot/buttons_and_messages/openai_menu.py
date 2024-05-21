import random
from pathlib import Path
from typing import List, Tuple, Union, Optional, Dict

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from django.conf import settings

from core.utils.i18n import I18N
from .base_classes import BaseButton, BaseMessage
from .contacts_buttons import ContactManagerButton
from ..config import SYMS
from ..utils.states import FSMMainMenuStates

AI_FIRST_GREETING = I18N(
    ru='Напишите ваш запрос. С чем у вас возникают проблемы? Где не хватает идей или фокуса?'
       ' Хотите описать ключевые зоны роста? Без проблем! Главное начать! Старайтесь разделять'
       ' большие запросы на небольшие конкретные части - тогда я буду максимально полезен для'
       ' вас. Не переживайте, первые ответы могут приходить с небольшой задержкой, но я учусь'
       ' быть побыстрее',
    en="Write your request. What are you having problems with? Where are ideas or focus"
       " lacking? Would you like to describe key growth areas? No problem! The main thing"
       " is to start! Try to divide large requests into small specific parts - then I will"
       " be most useful to you. Don't worry, the first answers may come with a slight delay,"
       " but I'm learning to be faster",
    common_right=SYMS.smile
)

AI_GREETINGS_LIST = [
    I18N(
        ru='Давайте поговорим',
        en="let's talk",
        common_right=SYMS.smile
    ),
    I18N(
        ru='У вас есть вопрос? Возникла проблема в команде?',
        en='Do you have a question? Having a problem with your team?',
    ),
    I18N(
        ru='Или просто хотите пообщаться. Я — только за',
        en="Or just want to chat. I am for it",
        common_right=SYMS.wink
    ),
    I18N(
        ru='Старайтесь говорить конкретно, так я лучше понимаю человеческую речь',
        en='Try to speak specifically, this way I understand human speech better',
    ),
    I18N(
        ru='Абстракции и метафизика пока немного не моё',
        en="Abstractions and metaphysics are a little not my thing yet",
        common_right=SYMS.laughter
    ),
    I18N(
        ru='Возможно, первое время я буду отвечать с небольшой задержкой или слегка невпопад.'
           ' Но я быстро учусь!',
        en="Perhaps at first I will answer with a slight delay or slightly out of place."
           " But I'm learning quickly!",
    ),
    I18N(
        ru='Давайте начнём. Напишите что-нибудь',
        en="Let's start. Write something",
        common_right=SYMS.down
    ),
]


class RegenerateAIResponse(BaseButton):
    """Кнопка Предложи другой вариант"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Предложи другой вариант',
            en='Ask an assistant a question',
            common_left=SYMS.repeat,
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

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
        try:
            wait_msg = await self.bot.send_message(
                chat_id=user_id, text=self.default_generate_answer
            )

            if ai_messages_data := await self.button_search_and_action_any_collections(
                    user_id=user_id,
                    action='get',
                    button_name='ai_messages_data',
                    updates_data=True
            ):

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
                ai_answer = settings.DEFAULT_FEED_ANSWER

            if ai_answer != settings.DEFAULT_FEED_ANSWER:
                reply_text = reply_text + ai_answer + ':ai:some_question'
            else:
                self.children_buttons = []
                reply_text = self.reply_text

            await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, self.next_state


class CreateNewTaskForQuestionOpenAI(BaseButton):
    """Кнопка старта нового задания"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Обсудить другую тему',
            en='Ask an assistant a question',
            common_left=SYMS.notes,
        )

    async def _set_answer_logic(
            self, update, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        reply_text = self.reply_text
        next_sate = self.next_state
        try:
            # удаляет сохранённый контекст при ошибке
            await self.button_search_and_action_any_collections(
                user_id=update.from_user.id, action='pop',
                button_name='ai_messages_data',
                updates_data=True
            )
            logic_button = QuestionOpenAI(new=False)
            self.children_buttons = logic_button.children_buttons
            reply_text, next_sate = await logic_button._set_answer_logic(update, state)
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_sate


class MessageOnceForQuestionOpenAIButton(BaseMessage):
    """Формирует ответ на вопрос заданный OpenAI"""

    def _set_state_or_key(self) -> str:
        return 'FSMMainMenuStates:question_openai'

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

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
        """I18N не используется из, за сложности хранения данных"""
        reply_text = self.reply_text
        self.children_buttons = [
            RegenerateAIResponse(new=False),
            CreateNewTaskForQuestionOpenAI(new=False),
            ContactManagerButton(new=False)
        ]
        try:
            reply_text = self.default_i_generate_text
            user_id = update.from_user.id

            if update.content_type == types.ContentType.VOICE:
                file_id = update.voice.file_id
            elif update.content_type == types.ContentType.AUDIO:
                file_id = update.audio.file_id
            else:
                file_id = None

            if file_id:
                file = await self.bot.get_file(file_id=file_id)
                file_on_disc = Path('media', f'{file_id}.wav')
                await self.bot.download_file(file_path=file.file_path, destination=file_on_disc)
                task_to_generate_ai = await self.ai.speech_to_text(file=file_on_disc)
            else:
                task_to_generate_ai = update.text.strip()

            wait_msg = await self.bot.send_message(chat_id=user_id,
                                                   text=self.default_generate_answer)

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

            if ai_answer != settings.DEFAULT_FEED_ANSWER:
                reply_text = reply_text + ai_answer + ':ai:some_question'

            else:
                # удаляет сохранённый контекст при ошибке
                await self.button_search_and_action_any_collections(
                    user_id=user_id, action='pop', button_name='ai_messages_data',
                    updates_data=True)
                self.children_buttons = []
                reply_text = self.reply_text

            await self.bot.delete_message(chat_id=user_id, message_id=wait_msg.message_id)

            user = update.user
            user.ai_dialog += (f'\n\n{SYMS.ask_assistant}\t\t{task_to_generate_ai}'
                               f'\n\n{reply_text.rstrip(":ai:some_question")}')
            await user.asave()
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, self.next_state


class QuestionOpenAI(BaseButton):
    """Класс описывающий кнопку - Задать вопрос OpenAI"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Задать вопрос ассистенту',
            en='Ask an assistant a question',
            common_left=SYMS.ask_assistant,
        )

    def _set_next_state(self) -> str:
        return FSMMainMenuStates.question_openai

    def _set_reply_text(self) -> Union[str, I18N]:
        return self.default_error

    async def _set_answer_logic(
            self, update: Message, state: FSMContext) -> Tuple[Union[str, Tuple], Optional[str]]:
        reply_text, next_state = self.reply_text, self.next_state
        user = update.user

        if not user.ai_dialog:
            reply_text = AI_FIRST_GREETING
        else:
            reply_text = random.choice(AI_GREETINGS_LIST)

        return SYMS.bot_face + reply_text, next_state

    def _set_messages(self) -> Dict:
        message = MessageOnceForQuestionOpenAIButton(parent_name=self.class_name)
        return {message.state_or_key: message}

    def _set_children(self) -> List:
        return [ContactManagerButton(new=False)]
