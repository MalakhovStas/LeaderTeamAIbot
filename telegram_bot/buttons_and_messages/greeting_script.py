"""Модуль формирования сценаярия первого знакомства с новым пользователем"""
from typing import Optional, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from company.models import Company
from users.models import User
from utils import utils
from .base_classes import Utils, BaseButton, BaseMessage
from ..config import FACE_BOT, COMPANY_ROLES
from ..utils.states import FSMGreetingScriptStates


class MessageGetContacts(BaseMessage, Utils):
    """Сообщение при изменении роли в компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_contacts'

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_reply_text(self) -> Optional[str]:
        return '<b>Благодарю за предоставленную информацию, начальные данные сохранены</b>'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        add_reply_text = "<b>⚠ Ошибка, контакт не сохранён</b>"
        try:
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            if email := await utils.data_to_email(update.text):
                user.email = email
                await user.asave()
                add_reply_text = "<b>Адрес электронной почты сохранён</b>"

            elif phone_number := await utils.data_to_phone(update.text):
                user.phone_number = phone_number
                await user.asave()
                add_reply_text = "<b>Номер телефона сохранён</b>"
        except Exception as exc:
            self.logger.error(exc)
        return f'{FACE_BOT}{add_reply_text}\n\n{self.reply_text}', self.next_state


class MessageGetRoleInCompany(BaseMessage, Utils):
    """Сообщение при изменении роли в компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_role_in_company'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_contacts

    def _set_reply_text(self) -> Optional[str]:
        return f"<b>Ваши контакты (телефон или e-mail)</b>"

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        try:
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
            if (num_role := await utils.data_to_str_digits(data=update.text)) \
                    and 1 <= int(num_role) <= len(COMPANY_ROLES):
                user.role_in_company = COMPANY_ROLES[int(num_role)]
            else:
                user.role_in_company = update.text
            await user.asave()
            add_reply_text = f'<b>Ваша роль в компании "{user.company.name}" сохранена</b>'
        except Exception as exc:
            self.logger.error(exc)
            add_reply_text = f'<b>⚠ Не удалось сохранить роль в компании</b>'
        return f'{FACE_BOT}{add_reply_text}\n\n{self.reply_text}', self.next_state

    def _set_messages(self) -> Dict:
        messages = [MessageGetContacts(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageGetAboutCommand(BaseMessage, Utils):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_about_command'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_role_in_company

    def _set_reply_text(self) -> Optional[str]:
        reply_text = (f'<b>Введите номер, соответствующий Вашей роли в компании '
                      f'согласно пунктам или введите текстом свой вариант:</b>\n\n')
        for num, role in COMPANY_ROLES.items():
            reply_text += f'{num}. {role}\n'
        return reply_text

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        try:
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()

            user.company.about_team = update.text
            await user.company.asave()
            add_reply_text = '<b>Информация о команде сохранена</b>'
        except Exception as exc:
            self.logger.error(exc)
            add_reply_text = '<b>⚠ Не удалось сохранить информацию о команде</b>'
        return f'{FACE_BOT}{add_reply_text}\n\n{self.reply_text}', self.next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetRoleInCompany()]}


class MessageGetAboutCompany(BaseMessage, Utils):
    """Сообщение при изменении информации о компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_about_company'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_about_command

    def _set_reply_text(self) -> Optional[str]:
        reply_text = (f'<b>Какая у вас команда? Опишите в свободной форме (сколько человек, '
                      'профессиональный и управленческий уровень членов команды и т.п.). Если '
                      'есть выраженная неоднородность в команде (например, разные поколения), '
                      'тоже напишите, это может быть важно.</b>\n\n')
        return reply_text

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        try:
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
            user.company.about_company = update.text
            await user.company.asave()
            add_reply_text = '<b>Информация о компании сохранена</b>'
        except Exception as exc:
            self.logger.error(exc)
            add_reply_text = '<b>⚠ Не удалось сохранить информацию о компании</b>'
        return f'{FACE_BOT}{add_reply_text}\n\n{self.reply_text}', self.next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetAboutCommand()]}


class MessageGetCompany(BaseMessage, Utils):
    """Сообщение при запросе от нового пользователя название компании"""
    message_get_about_company = [MessageGetAboutCompany()]
    message_get_role_in_company = [MessageGetRoleInCompany()]

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_company'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = 'reset_state'
        reply_text = "<b>⚠ Ошибка регистрации компании</b>"
        try:
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            company, fact_create = await Company.objects.aget_or_create(name=update.text)
            user.company = company
            await user.asave()

            if company and fact_create:
                reply_text = (
                    f'<b>Компания "{company.name}" успешно зарегистрирована\n\n'
                    f'Опишите вашу компанию (ниша, размер и тп)</b>')
                next_state = FSMGreetingScriptStates.get_about_company
                self.children_messages = {message.state_or_key: message
                                          for message in self.message_get_about_company}
            elif company and not fact_create:
                reply_text = (
                    f'<b>Компания "{company.name}" ранее зарегистрирована, Вы добавлены в список '
                    'участников\n\nВведите номер, соответствующий Вашей роли в компании '
                    'согласно пунктам или введите текстом свой вариант:</b>\n\n')
                for num, role in COMPANY_ROLES.items():
                    reply_text += f'{num}. {role}\n'
                next_state = FSMGreetingScriptStates.get_role_in_company
                self.children_messages = {message.state_or_key: message
                                          for message in self.message_get_role_in_company}
        except Exception as exc:
            self.logger.error(exc)
        return FACE_BOT + reply_text, next_state


class MessageGetFullname(BaseMessage, Utils):
    """Сообщение при старте знакомства с новым пользователем"""
    message_get_company = [MessageGetCompany()]
    message_get_role_in_company = [MessageGetRoleInCompany()]

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_fullname'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text = '<b>Введите название Вашей компании?</b>'
        next_state = FSMGreetingScriptStates.get_company
        self.children_messages = {message.state_or_key: message
                                  for message in self.message_get_company}

        add_reply_text = '<b>⚠ Не удалось сохранить ФИО</b>'
        try:
            name, surname, patronymic = utils.get_fullname(update.text)
            # изменён порядок на имя, фамилию отчество
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
            user.name = name
            user.surname = surname
            user.patronymic = patronymic
            await user.asave()
            if surname and name and patronymic:
                add_reply_text = '<b>Ваши ФИО сохранены</b>'
            elif surname and name:
                add_reply_text = '<b>Ваши Имя и Фамилия сохранены</b>'
            else:
                add_reply_text = '<b>Ваше Имя сохранено</b>'
            if user.company:
                reply_text = (f'<b>Введите номер, соответствующий Вашей роли в компании '
                              f'согласно пунктам или введите текстом свой вариант:</b>\n\n')
                for num, role in COMPANY_ROLES.items():
                    reply_text += f'{num}. {role}\n'
                next_state = FSMGreetingScriptStates.get_role_in_company
                self.children_messages = {message.state_or_key: message
                                          for message in self.message_get_role_in_company}
        except Exception as exc:
            self.logger.error(exc)
        return f'{FACE_BOT}{add_reply_text}\n\n{reply_text}', next_state


class StartGreetingButton(BaseButton):
    """Класс описывающий кнопку - Познакомится"""

    def _set_name(self) -> str:
        return '🏢 \t Познакомится'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_fullname

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + ('Для начала, расскажите немного про себя, свою компанию и команду. '
                           'Данные о Вас и Вашей компании будут сохранены в профиле и помогут мне,'
                           'как Ассистенту максимально эффективно работать с Вашими запросами. '
                           'При необходимости Вы сможете внести изменения в свой профиль.\n\n'
                           'Как вас зовут? '
                           '(введите через пробел ваше Имя Фамилию и Отчество в таком порядке)')

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message
                for message in [MessageGetFullname(parent_name=self.class_name)]}
