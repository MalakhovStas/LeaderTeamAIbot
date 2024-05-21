from typing import Union, Any, Optional, Tuple

from django.conf import settings

from users.models import User


class TranslationError(Exception):
    """Исключение для выделения ошибок связанных с интернационализацией сообщений от бота"""


class I18N:
    """Класс для интернационализации сообщений от бота пользователям"""

    def __init__(
            self,
            en,
            ru,
            common_left: str = '',
            common_right: str = '',
            style: Optional[str] = None,
            common_style: Optional[str] = None,
            general_style: Optional[str] = None):

        ru, en, common_left, common_right = self.apply_styles(
            en=en, ru=ru, common_left=common_left, common_right=common_right,
            style=style, common_style=common_style, general_style=general_style
        )

        self.ru = common_left + ru + common_right
        self.en = common_left + en + common_right

    def __add__(self, other: 'I18N') -> 'I18N':
        """Метод для конкатенации с правым операндом"""
        if self.check_object(other):
            if isinstance(other, str):
                return I18N(en=self.en + other, ru=self.ru + other)
            elif isinstance(other, I18N):
                return I18N(en=self.en + other.en, ru=self.ru + other.ru)

    def __radd__(self, other):
        """Метод для конкатенации с левым операндом"""
        if self.check_object(other):
            if isinstance(other, str):
                return I18N(en=other + self.en, ru=other + self.ru)
            elif isinstance(other, I18N):
                return I18N(en=other.en + self.en, ru=other.ru + self.ru)

    def __iadd__(self, other):
        """Метод для реализации выражения +="""
        if self.check_object(other):
            if isinstance(other, str):
                self.en += other
                self.ru += other
            elif isinstance(other, I18N):
                self.en += other.en
                self.ru += other.ru
        return self

    @staticmethod
    def apply_styles(
            en,
            ru,
            common_left: str = '',
            common_right: str = '',
            style: Optional[str] = None,
            common_style: Optional[str] = None,
            general_style: Optional[str] = None,
    ) -> Tuple[str, str, str, str]:
        """Метод для применения стилей"""
        bold_symbols = ['B', 'b', 'bold']
        italic_symbols = ['I', 'i', 'italic']
        bold_italic_symbols = ['BI', 'bi', 'bold_italic']

        if style:
            if style in bold_symbols:
                ru = f'<b>{ru}</b>'
                en = f'<b>{en}</b>'

            elif style in italic_symbols:
                ru = f'<i>{ru}</i>'
                en = f'<i>{en}</i>'

            elif style in bold_italic_symbols:
                ru = f'<b><i>{ru}</i></b>'
                en = f'<b><i>{en}</i></b>'

        elif common_style:
            if common_style in bold_symbols:
                common_left = f'<b>{common_left}</b>'
                common_right = f'<b>{common_right}</b>'

            elif common_style in italic_symbols:
                common_left = f'<i>{common_left}</i>'
                common_right = f'<i>{common_right}</i>'

            elif common_style in bold_italic_symbols:
                common_left = f'<b><i>{common_left}</i></b>'
                common_right = f'<b><i>{common_right}</i></b>'

        if general_style:
            if general_style in bold_symbols:
                ru = f'<b>{ru}</b>'
                en = f'<b>{en}</b>'
                common_left = f'<b>{common_left}</b>'
                common_right = f'<b>{common_right}</b>'

            elif general_style in italic_symbols:
                ru = f'<i>{ru}</i>'
                en = f'<i>{en}</i>'
                common_left = f'<i>{common_left}</i>'
                common_right = f'<i>{common_right}</i>'

            elif general_style in bold_italic_symbols:
                ru = f'<b><i>{ru}</i></b>'
                en = f'<b><i>{en}</i></b>'
                common_left = f'<b><i>{common_left}</i></b>'
                common_right = f'<b><i>{common_right}</i></b>'

        return ru, en, common_left, common_right

    @staticmethod
    def check_object(other: Any) -> bool:
        """Проверка переданного объекта на соответствие классу I18N"""
        if not isinstance(other, (I18N, str)):
            raise TranslationError('Некорректный операнд, для конкатенации '
                                   'необходимо передать экземпляр класса I18N или str')
        return True
        
    def translate(self, language_code: str) -> str:
        """Метод для интернационализации данных экземпляра класса"""
        if language_code == 'ru':
            result = self.ru
        elif language_code == 'en':
            result = self.en
        else:
            raise TranslationError(f'Неизвестный language_code: {language_code}')
        return result

    @staticmethod
    async def switch_language(user: User) -> str:
        """Метод для переключения языка пользователя между ru/en"""
        if user.language == 'ru':
            user.language = 'en'
            await user.asave()
            result = 'en'
        elif user.language == 'en':
            user.language = 'ru'
            await user.asave()
            result = 'ru'
        else:
            raise TranslationError(
                f'У пользователя {user} установлен неизвестный language_code: {user.language}'
            )
        return result

    @staticmethod
    async def change_language(user: User, target_language: str) -> str:
        """Метод для изменения языка пользователя на target_language"""
        if target_language in [lang[0] for lang in settings.LANGUAGES]:
            user.language = target_language
            await user.asave()
        else:
            raise TranslationError(f'Указан неизвестный target_language: {target_language}')
        return target_language

    @staticmethod
    def translate_button(button_name: Union[str, 'I18N'], user: User) -> str:
        """Интернационализация названий кнопок"""
        if isinstance(button_name, I18N):
            button_name = button_name.translate(user.language)
        return button_name

    @staticmethod
    def translate_reply_text(reply_text: Union[str, 'I18N'], user: User) -> str:
        """Интернационализация сообщений от бота пользователю"""
        if isinstance(reply_text, I18N):
            reply_text = reply_text.translate(user.language)
        return reply_text
