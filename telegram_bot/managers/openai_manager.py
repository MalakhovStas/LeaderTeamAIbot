"""Модуль инструментов для взаимодействия с библиотекой и сервисом OpenAI"""
import asyncio
from typing import Sequence, Optional, Union, List, Tuple, Dict

import openai
from aiogram.types import CallbackQuery, Message

from ..config import (
    OpenAI_TOKEN,
    OpenAI_ORGANIZATION,
    OpenAI_PROXY,
    INVITATION,
    ASSISTANT_PROMPT,
    MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    TOP_P,
    PRESENCE_PENALTY,
    FREQUENCY_PENALTY,
    TIMEOUT,
    DEFAULT_FEED_ANSWER,
    DEFAULT_NOT_ENOUGH_BALANCE,
    DEBUG
)
from ..models import TelegramAccount


class OpenAIManager:
    """ Класс для работы с API ChatGPT """
    __instance = None
    __default_bad_answer = DEFAULT_FEED_ANSWER

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, dbase, bot, logger):
        self.openai = openai
        self.openai.organization = OpenAI_ORGANIZATION
        self.openai.api_key = OpenAI_TOKEN
        self.openai.proxy = OpenAI_PROXY
        self.dbase = dbase
        self.bot = bot
        self.logger = logger
        self.sign = self.__class__.__name__ + ': '

    @staticmethod
    async def prompt_correct(text: str) -> str:
        """Для корректировки входящего запроса, в конце обязательно должна стоять точка,
        иначе модель ИИ пытается продолжить текст, а не ответить на него"""
        text = text.strip()
        if not text.endswith('.'):
            text += '.'
        return f'{INVITATION} {text}'

    async def check_user_balance_requests(
            self, user_id, update: Union[CallbackQuery, Message, None] = None) -> bool:
        user = await TelegramAccount.objects.filter(tg_user_id=user_id).afirst()
        if user and user.balance_requests > 0:
            return True
        # if isinstance(update, CallbackQuery):
        #     ...
        # await self.bot.answer_callback_query(callback_query_id=update.id, show_alert=False,
        #                                      text=DEFAULT_NOT_ENOUGH_BALANCE)
        if DEBUG:
            self.logger.warning(self.sign + f"{user_id=} | {user.tg_username=} | "
                                            f"{user.balance_requests=} | "
                                            f"answer: {DEFAULT_NOT_ENOUGH_BALANCE[:100]}...")
        return False

    async def answer_davinchi(self, prompt: str, correct: bool = True,
                              user_id: Union[int, str, None] = None,
                              update: Union[CallbackQuery, Message, None] = None) -> str:
        """ Запрос к ChatGPT модель: text-davinci-003 """
        if not await self.check_user_balance_requests(user_id=user_id, update=update):
            return DEFAULT_NOT_ENOUGH_BALANCE

        prompt = await self.prompt_correct(text=prompt) if correct else prompt
        if DEBUG:
            self.logger.info(self.sign + f"question: {prompt[:100]}...")
        try:
            response = await asyncio.wait_for(self.openai.Completion.acreate(
                model=MODEL,
                prompt=prompt,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                presence_penalty=PRESENCE_PENALTY,
                frequency_penalty=FREQUENCY_PENALTY,
                timeout=TIMEOUT
            ), timeout=TIMEOUT + 3)

            if response and isinstance(response.get('choices'), Sequence):
                answer = response['choices'][0]['text'].strip('\n')
                await self.dbase.update_user_balance_requests(user_id=user_id, down_balance=1)
            else:
                answer = self.__default_bad_answer

        except Exception as exception:
            # from ..utils.admins_send_message import func_admins_message
            # await func_admins_message(exc=f'{self.sign} {exception=}')
            if DEBUG:
                self.logger.warning(self.sign + f"{exception=}")
            # TODO Убрать сообщение об исключении пользователю
            answer = self.__default_bad_answer

        text = answer.replace('\n', '')
        if DEBUG:
            self.logger.info(self.sign + f"answer: {text[:100]}...")
        return answer

    async def answer_gpt_3_5_turbo(
            self,
            prompt: str,
            correct: bool = True,
            messages_data: Optional[List] = None,
            user_id: Union[int, str, None] = None,
            update: Union[CallbackQuery, Message, None] = None) -> str:
        """ Запрос к ChatGPT модель: gpt-3.5-turbo"""
        if not await self.check_user_balance_requests(user_id=user_id, update=update):
            return DEFAULT_NOT_ENOUGH_BALANCE

        prompt = await self.prompt_correct(text=prompt) if correct else prompt
        if DEBUG:
            self.logger.info(self.sign + f"question: {prompt[:100]}...")

        messages_data = list() if not isinstance(messages_data, list) else messages_data
        if not messages_data:
            # добавляет начальный prompt для настройки ИИ бота
            messages_data.append({"role": "assistant", "content": ASSISTANT_PROMPT})

        messages_data.append({"role": "user", "content": prompt})

        try:
            # print(MODEL)
            # print(messages_data)
            # print(self.openai.organization)
            # print(self.openai.api_key)
            # print(messages_data)
            response = await asyncio.wait_for(self.openai.ChatCompletion.acreate(
                model=MODEL,
                messages=messages_data,
                timeout=TIMEOUT
            ), timeout=TIMEOUT + 3)

            if response and isinstance(response.get('choices'), Sequence):
                answer = response['choices'][0]['message']['content'].strip('\n')
                messages_data.append({"role": "assistant", "content": answer})
                await self.dbase.update_user_balance_requests(user_id=user_id, down_balance=1)
            else:
                messages_data.pop(-1)
                answer = self.__default_bad_answer

        except Exception as exception:
            # await func_admins_message(exc=f'{self.sign} {exception=}')
            if DEBUG:
                self.logger.warning(self.sign + f"{exception=}")
            answer = self.__default_bad_answer

        text = answer.replace('\n', '')
        if DEBUG:
            self.logger.info(self.sign + f"answer: {text[:100]}...")
        return answer

    async def generate_image_from_text(self, prompt):
        """ Сгенерированные изображения могут иметь размер 256x256, 512x512 или 1024x1024 пикселей.
        Меньшие размеры генерируются быстрее. Вы можете запросить от 1 до 10 изображений за раз,
        используя параметр n """

        response = await openai.Image.acreate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url

    @classmethod
    async def _check_type_str(cls, *args) -> bool:
        return all((isinstance(arg, str) for arg in args))

    async def reply_feedback(
            self,
            feedback: str,
            feed_name: Optional[str] = None,
            user_id: Union[int, str, None] = None,
            update: Union[CallbackQuery, Message, None] = None) -> Union[Tuple, str]:
        answer = None
        if await self._check_type_str(feedback):
            if MODEL == 'gpt-3.5-turbo':
                answer = await self.answer_gpt_3_5_turbo(
                    prompt=feedback, user_id=user_id, update=update)
            else:
                answer = await self.answer_davinchi(
                    prompt=feedback, user_id=user_id, update=update)

        if feed_name:
            return feed_name, answer
        else:
            return answer

    async def some_question(
            self,
            prompt: str,
            messages_data: Optional[List] = None,
            user_id: Union[int, str, None] = None,
            update: Union[CallbackQuery, Message, None] = None) -> str:

        if await self._check_type_str(prompt):
            if MODEL == 'gpt-3.5-turbo':
                answer = await self.answer_gpt_3_5_turbo(
                    prompt=prompt,
                    correct=False,
                    messages_data=messages_data,
                    user_id=user_id,
                    update=update
                )
            else:
                answer = await self.answer_davinchi(
                    prompt=prompt, correct=False, user_id=user_id, update=update)
            return answer

    async def automatic_generate_answer_for_many_feeds(
            self, feedbacks: Dict, user_id: Union[int, str, None] = None) -> Dict:
        # TODO настроить проверку баланса
        data = [self.reply_feedback(
            feedback=feed_data.get('text'), feed_name=feed_name, user_id=user_id)
            for feed_name, feed_data in feedbacks.items()]

        list_result = await asyncio.gather(*data)
        await asyncio.sleep(0.1)
        [feedbacks.get(feed_name).update({'answer': answer}) for feed_name, answer in list_result]

        return feedbacks

# Так выглядит ответ
# {
#   "choices": [
#     {
#       "finish_reason": "stop",
#       "index": 0,
#       "logprobs": null,
#       "text": "Тут текст ответа"
#     }
#   ],
#   "created": 1679239442,
#   "id": "cmpl-6vpB47cqEu53oWtRauBAbZ5IVK2cS",
#   "model": "text-davinci-003",
#   "object": "text_completion",
#   "usage": {
#     "completion_tokens": 270,
#     "prompt_tokens": 134,
#     "total_tokens": 404
#   }
# }
