from abc import ABC
from typing import Any, Optional, Union, List, Tuple, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from .. import config
from core.utils.i18n import I18N
from django.conf import settings


class Base(ABC):
    """Базовый класс для всех кнопок и сообщений"""
    ai = None  # Добавляется в loader.py
    bot = None  # Добавляется в loader.py
    pay_sys = None  # Добавляется в loader.py

    logger = logger
    exception_controller = None  # Добавляется в loader.py

    reset_state = 'reset_state'
    default_error = config.DEFAULT_ERROR

    default_bad_text = config.DEFAULT_BAD_TEXT
    default_service_in_dev = config.DEFAULT_SERVICE_IN_DEV
    default_incorrect_data_input_text = config.DEFAULT_INCORRECT_DATA_INPUT_TEXT
    default_generate_answer = config.DEFAULT_GENERATE_ANSWER
    default_choice_menu = config.DEFAULT_CHOICE_MENU
    default_i_generate_text = config.DEFAULT_I_GENERATE_TEXT
    default_text_for_payment_link = config.DEFAULT_TEXT_FOR_PAYMENT_LINK

    # Как выглядит словарь
    # general_collection = {
    #     'general_messages': {},
    #     'general_buttons': {},
    #     'user_id': {'updates_data': {}, 'suppliers': {}, 'feedbacks': {}, 'aufm_catalog': {}}
    # }

    general_collection = dict()
    general_collection_dump = dict()

    def log(self, message, level: Optional[str] = None):
        text = f'class: {self.__class__.__name__}: {message}'

        level = 'debug' if not level else level

        if level.lower() == 'info':
            if settings.DEBUG:
                self.logger.info(text)

        elif level.lower() == 'warning':
            if settings.DEBUG:
                self.logger.warning(text)

        elif level.lower() == 'error':
            if settings.DEBUG:
                self.logger.error(text)

        else:
            if settings.DEBUG:
                self.logger.debug(text)

    def _set_reply_text(self) -> Union[str, I18N]:
        """Установка текста ответа """
        reply_text = 'Default: reply_text not set -> override method _set_reply_text ' \
                     'in class' + self.__class__.__name__
        return reply_text

    def _set_next_state(self) -> Optional[str]:
        """Установка следующего состояния по умолчанию None"""
        return None

    def _set_children(self) -> list:
        """ Установка дочерних кнопок по умолчанию list()"""
        return list()

    @classmethod
    async def get_many_buttons_from_any_collections(
            cls, get_buttons_list: Union[List, Tuple],
            user_id: Optional[int] = None) -> Optional[Any]:
        if settings.DEBUG:
            cls.logger.debug(f'Base: get_many_buttons_from_any_collections -> '
                             f'get_buttons_list: {get_buttons_list}')
        result_buttons_list = list()

        if get_buttons_list:
            for button_name in get_buttons_list:
                if button_name:

                    if result_button := await cls.button_search_and_action_any_collections(
                            user_id=user_id, action='get', button_name=button_name):

                        result_buttons_list.append(result_button)

        if result_buttons_list:
            if settings.DEBUG:
                cls.logger.debug(f'Base:-> OK -> {get_buttons_list=} '
                                 f'| return {result_buttons_list=}')
        else:
            if settings.DEBUG:
                cls.logger.warning(f'Base: -> BAD -> {get_buttons_list=} '
                                   f'| return {result_buttons_list=}')

        # result_buttons_list.append(GoToBack(new=False))
        return result_buttons_list

    @classmethod
    async def button_search_and_action_any_collections(
            cls, action: str,
            button_name: Optional[str] = None,
            instance_button: Union[Any, str, None] = None,
            user_id: Union[str, int, None] = None,
            update: Union[Message, CallbackQuery, None] = None,
            message: bool = False,
            updates_data: bool = False,
            aufm_catalog_key: Optional[str] = None
            ) -> Optional[Any]:

        # print('@base_classes.py@:', cls.general_collection)

        if update and not user_id:
            user_id = update.from_user.id
        user_id = str(user_id)

        if aufm_catalog_key:
            if action == 'add':
                cls.general_collection.setdefault(user_id, dict()).setdefault(
                    'aufm_catalog', dict())[aufm_catalog_key] = button_name
                return True
            elif action == 'pop':
                cls.general_collection.setdefault(user_id, dict()).setdefault(
                    'aufm_catalog', dict()).pop(aufm_catalog_key, None)
                action = 'get'
            else:
                raise ValueError(f'aufm_catalog не поддерживает {action=}')

        if not button_name and not instance_button:
            if settings.DEBUG:
                cls.logger.error(f'Чтобы выполнить {action=} необходимо передать button_name или '
                                 f'instance_button {updates_data=} | {aufm_catalog_key=}')
            button_name = 'MainMenu'

        if instance_button and not aufm_catalog_key and not updates_data:
            button_name = instance_button.class_name

        # if button_name.startswith('Supplier'):
        #     collection_name = 'suppliers'

        # elif button_name.startswith('Feedback'):
        #     collection_name = 'feedbacks'

        else:
            if message:
                collection_name = 'general_messages'
            elif updates_data:
                collection_name = 'updates_data'
            else:
                collection_name = 'general_buttons'

        if action == 'add':
            if instance_button or updates_data:
                if collection_name in ['general_buttons', 'general_messages']:
                    cls.general_collection.setdefault(collection_name, dict())[
                        button_name] = instance_button
                else:
                    cls.general_collection.setdefault(user_id, dict()).setdefault(
                        collection_name, dict())[button_name] = instance_button

                button = instance_button
            else:
                raise ValueError(f'Чтобы выполнить {action=} в {collection_name=}, '
                                 f'необходимо передать instance_button -> {button_name=}')
        elif action == 'get':
            if collection_name in ['general_buttons', 'general_messages']:
                button = cls.general_collection.setdefault(
                    collection_name, dict()).get(button_name)
            else:
                button = cls.general_collection.setdefault(user_id, dict()).setdefault(
                    collection_name, dict()).get(button_name)
        elif action == 'pop':
            if collection_name in ['general_buttons', 'general_messages']:
                button = cls.general_collection.setdefault(
                    collection_name, dict()).pop(button_name, None)
            else:
                button = cls.general_collection.setdefault(user_id, dict()).setdefault(
                    collection_name, dict()).pop(button_name)
        else:
            button = None

        if button:
            if settings.DEBUG:
                cls.logger.debug(f'Base:-> OK -> {action=} | {button_name=} '
                                 f'| {collection_name=} | return {button=}')
        else:
            if settings.DEBUG:
                cls.logger.warning(f'Base: -> BAD -> {action=} | {button_name=} '
                                   f'| {collection_name=} | return {button=}')

        return button


class BaseMessage(Base):
    """ Логика - которая будет прописана в дочерних классах выполниться только один раз
    при старте программы динамическая логика должна быть прописана в методе _set_answer_logic.
    Каждое сообщение при создании автоматически добавляется в коллекцию на основе префикса"""

    __instance = None
    base_sign = 'BaseMessage: '

    __slots__ = ('class_name',  'parent_name', 'state_or_key',
                 'reply_text', 'children_buttons', 'next_state')

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, state_or_key: Optional[str] = None, reply_text: Optional[str] = None,
                 children_buttons: Optional[List] = None, parent_name: Optional[str] = None,
                 messages: Optional[Dict] = None):

        if self.__class__.__name__ != BaseMessage.__name__:
            self.class_name = self.__class__.__name__
            self.parent_name = parent_name if parent_name else None
            self.state_or_key = self._set_state_or_key() if not state_or_key else state_or_key
            self.reply_text = self._set_reply_text() if not reply_text else reply_text
            self.children_buttons = self._set_children() if not children_buttons else children_buttons
            self.children_messages = self._set_messages() if not messages else messages

            self.next_state = self._set_next_state()
            self.general_collection.setdefault('general_messages', dict())[self.state_or_key] = self

    def __str__(self):
        return (f'message: {self.class_name} | {self.state_or_key} | '
                f'reply_text: {self.reply_text[:15]}... | children: '
                f'{[f"< {child.class_name}: {child.name} >" for child in self.children_buttons]}')

    def _set_state_or_key(self) -> str:
        """ Установка состояния или ключа по которому вызывается дочерний класс
        для обработки входящего сообщения """
        reply_text = ('Default: state_or_key not set -> '
                      'override method _set_state_or_key in class') + self.class_name
        return reply_text

    def _set_messages(self) -> Dict:
        return dict()


class BaseButton(Base):
    """ Логика - которая будет прописана в дочерних классах выполниться только один раз при
    старте программы динамическая логика должна быть прописана в методе _set_answer_logic.
    Каждая кнопка при создании автоматически добавляется в коллекцию на основе префикса"""

    __instance = None
    __buttons_id = [0, ]
    base_sign = 'BaseButton: '

    __slots__ = ('class_name', 'user_id', 'parent_name', 'name', 'url', 'callback',
                 'parent_button', 'reply_text', 'next_state', 'any_data', 'children_buttons',
                 'children_messages')

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, user_id: Optional[str] = None, parent_name: Optional[str] = None,
                 name: Optional[str] = None, callback: Optional[str] = None,
                 parent_button: Optional[Any] = None, reply_text: Optional[str] = None,
                 next_state: Optional[str] = None, any_data: Optional[Dict] = None,
                 children: Optional[List] = None, messages: Optional[Dict] = None,
                 new: bool = True):

        user_id = str(user_id) if user_id else None
        if new and self.__class__.__name__ != BaseButton.__name__:
            self.class_name = self.__class__.__name__
            self.user_id = user_id
            self.parent_name = parent_name
            self.name = self._set_name() if not name else name
            self.url = self._set_url()
            self.callback = self._set_callback() if not callback else callback
            self.parent_button = parent_button
            self.reply_text = self._set_reply_text() if not reply_text else reply_text
            self.next_state = self._set_next_state() if not next_state else next_state
            self.any_data = any_data

            self.children_buttons = self._set_children() if not children else children
            self.children_messages = self._set_messages() if not messages else messages

            self.general_collection.setdefault('general_buttons', dict())[self.class_name] = self

    def __str__(self):
        return (f'button: {self.class_name=} | {self.name=} | {self.callback=} | '
                f'{self.parent_name=} | reply_text={self.reply_text[:15]}... | children: '
                f'{[f"< {child.class_name}: {child.name} >" for child in self.children_buttons]} |'
                f'messages: {[f"< {message.class_name}: {message.state_or_key} >" for message in self.children_messages.values()]}')

    def _set_name(self) -> Union[str, I18N]:
        name = 'Button:' + self.class_name
        return name

    def _set_callback(self) -> Optional[str]:
        if self.url:
            return None
        return self.class_name

    def _set_url(self) -> Optional[str]:
        return None

    def _set_messages(self) -> Dict:
        return dict()


class GoToBack(BaseButton):
    def _set_name(self) -> str:
        return '◀ \t Назад'

    async def _set_answer_logic(self, update, state: Optional[FSMContext] = None):
        user_id = update.from_user.id

        result_button = await self.button_search_and_action_any_collections(
            user_id=user_id, action='get', button_name='PersonalCabinet')

        if previous_button_name := await self.button_search_and_action_any_collections(
                user_id=user_id, action='get', button_name='previous_button', updates_data=True):

            if previous_button := await self.button_search_and_action_any_collections(
                    user_id=user_id, action='get', button_name=previous_button_name):

                if hasattr(previous_button, 'parent_name') and previous_button.parent_name:
                    result_button = await self.button_search_and_action_any_collections(
                        user_id=user_id, action='get', button_name=previous_button.parent_name)

        if hasattr(result_button.__class__, '_set_answer_logic'):
            reply_text, next_state = await result_button._set_answer_logic(update, state)
        else:
            reply_text, next_state = result_button.reply_text, result_button.next_state

        self.children_buttons = result_button.children_buttons
        update.data = result_button.class_name
        return reply_text, next_state


class Utils(Base):
    """Класс дополнительных инструментов для реализации меню"""
    list_children_buttons = [GoToBack()]
    # greeting_button_script = StartGreetingButton()