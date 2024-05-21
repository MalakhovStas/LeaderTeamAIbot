"""Модуль инструментов для взаимодействия с библиотекой и сервисом OpenAI"""
import asyncio
import os
from typing import Optional, Union, List

from aiogram.types import CallbackQuery, Message
# from asgiref.sync import sync_to_async
from django.conf import settings
from httpx import AsyncClient
from openai import AsyncOpenAI
from openai.types.audio.transcription import Transcription
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from config import openai_settings
from ..models import TelegramAccount
from ..utils.admins_send_message import func_admins_message
# from importlib import reload


class OpenAIManager:
    """ Класс для работы с API ChatGPT """
    __instance = None
    __default_bad_answer = openai_settings.DEFAULT_ANSWER

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, dbase, bot, logger):

        self.openai = AsyncOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            organization=openai_settings.OPENAI_ORGANIZATION,
            http_client=AsyncClient(proxy=openai_settings.OPENAI_PROXY)
        )
        self.dbase = dbase
        self.bot = bot
        self.logger = logger
        self.sign = self.__class__.__name__ + ': '

    async def some_question(
            self,
            prompt: str,
            messages_data: Optional[List] = None,
            user_id: Union[int, str, None] = None,
            update: Union[CallbackQuery, Message, None] = None) -> Optional[str]:
        """Основной метод осуществления запросов к ChatGPT"""
        # await sync_to_async(reload)(openai_settings)
        answer = None
        if await self._check_type_str(prompt):
            if openai_settings.OPENAI_MODEL == 'gpt-3.5-turbo':
                answer = await self.answer_gpt_3_5_turbo(
                    prompt=prompt,
                    correct=False,
                    messages_data=messages_data,
                    user_id=user_id,
                    update=update
                )
        return answer

    @staticmethod
    async def _check_type_str(*args) -> bool:
        return all((isinstance(arg, str) for arg in args))

    @staticmethod
    async def prompt_correct(text: str) -> str:
        """Для корректировки входящего запроса, в конце обязательно должна стоять точка,
        иначе модель ИИ пытается продолжить текст, а не ответить на него"""
        text = text.strip()
        if not text.endswith('.'):
            text += '.'
        return f'{openai_settings.INVITATION} {text}'

    async def check_user_balance_requests(
            self, user_id, update: Union[CallbackQuery, Message, None] = None) -> bool:
        """Проверка доступного баланса пользователей"""
        user = await TelegramAccount.objects.filter(
            tg_user_id=user_id or update.from_user.id).afirst()
        if user and user.balance_requests > 0:
            return True
        # if isinstance(update, CallbackQuery):
        #     ...
        # await self.bot.answer_callback_query(callback_query_id=update.id, show_alert=False,
        #                                      text=openai_settings.DEFAULT_NOT_ENOUGH_BALANCE)
        if settings.DEBUG:
            self.logger.warning(self.sign + f"{user_id=} | {user.tg_username=} | "
                                            f"{user.balance_requests=} | "
                                            f"answer: {openai_settings.DEFAULT_NOT_ENOUGH_BALANCE[:100]}"
                                            f"...")
        return False

    async def answer_gpt_3_5_turbo(
            self,
            prompt: str,
            correct: bool = True,
            messages_data: Optional[List] = None,
            user_id: Union[int, str, None] = None,
            update: Union[CallbackQuery, Message, None] = None) -> str:
        """ Запрос к ChatGPT модель: gpt-3.5-turbo"""
        if not await self.check_user_balance_requests(user_id=user_id, update=update):
            return openai_settings.DEFAULT_NOT_ENOUGH_BALANCE

        prompt = await self.prompt_correct(text=prompt) if correct else prompt
        if settings.DEBUG:
            self.logger.info(self.sign + f"question: {prompt[:100]}...")

        messages_data = list() if not isinstance(messages_data, list) else messages_data
        if not messages_data:
            # добавляет начальный prompt для настройки ИИ бота
            messages_data.append(
                {"role": "assistant", "content": openai_settings.ASSISTANT_PROMPT})

        messages_data.append({"role": "user", "content": prompt})

        try:
            response = await asyncio.wait_for(self.openai.chat.completions.create(
                model=openai_settings.OPENAI_MODEL,
                messages=messages_data,
                timeout=openai_settings.OPENAI_TIMEOUT
            ), timeout=openai_settings.OPENAI_TIMEOUT + 3)

            if (response
                    and isinstance(response, ChatCompletion)
                    and isinstance(response.choices[0], Choice)
                    and isinstance(response.choices[0].message, ChatCompletionMessage)
            ):
                answer = response.choices[0].message.content.strip('\n')
                messages_data.append({"role": "assistant", "content": answer})
                await self.dbase.update_user_balance_requests(user_id=user_id, down_balance=1)
            else:
                messages_data.pop(-1)
                answer = self.__default_bad_answer

        except Exception as exception:
            await func_admins_message(exc=f'{self.sign} {exception=}')
            if settings.DEBUG:
                self.logger.warning(self.sign + f"{exception=}")
            answer = self.__default_bad_answer

        text = answer.replace('\n', '')
        if settings.DEBUG:
            self.logger.info(self.sign + f"answer: {text[:100]}...")
        return answer

    async def speech_to_text(self, file) -> str:
        """Транскрибирует голосовое сообщение или звуковой файл в естественный текст"""
        result = 'transcription error'
        # await sync_to_async(reload)(openai_settings)
        try:
            audio = open(file, 'rb')
            transcription: Transcription = await asyncio.wait_for(
                self.openai.audio.transcriptions.create(model="whisper-1", file=audio),
                timeout=openai_settings.OPENAI_TIMEOUT + 3
            )
            os.remove(file)
            result = transcription.text.strip()
        except Exception as exception:
            await func_admins_message(exc=f'{self.sign} {result=} {exception=}')
            if settings.DEBUG:
                self.logger.warning(f'{self.sign} {result=} {exception=}')
        return result
