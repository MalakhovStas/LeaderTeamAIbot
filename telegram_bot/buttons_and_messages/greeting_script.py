"""Модуль формирования сценаярия первого знакомства с новым пользователем"""
from typing import Optional, Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from django.conf import settings

from company.models import Company
from core.utils.i18n import I18N
from utils import utils
from .base_classes import Utils, BaseButton, BaseMessage
from ..config import SYMS, DEFAULT_GREETING
from ..utils.states import FSMGreetingScriptStates


class MessageGetContacts(BaseMessage, Utils):
    """Сообщение при изменении роли в компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_contacts'

    def _set_next_state(self) -> str:
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Благодарю за предоставленную информацию, начальные данные сохранены',
            en='Thank you for the information provided, the initial data has been saved',
            style='bold',
        )

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        add_reply_text = I18N(
            ru='Не удалось сохранить контакт',
            en='Failed to save contact',
            style='bold',
            common_left=SYMS.warning,
            common_right='\n\n',
        )
        try:
            if email := await utils.data_to_email(update.text):
                user.email = email
                await user.asave()

            elif phone_number := await utils.data_to_phone(update.text):
                user.phone_number = phone_number
                await user.asave()
            add_reply_text = I18N(
                ru='Вношу в свой блокнотик, спасибо',
                en="I'll add it to my notebook, thanks",
                common_right=SYMS.smile + '\n\n',
            )
        except Exception as exc:
            self.log(message=exc, level='error')
        return add_reply_text + self.reply_text, self.next_state


class MessageGetRoleInCompany(BaseMessage, Utils):
    """Сообщение при изменении роли в компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_role_in_company'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_contacts

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru=f'Отлично, теперь я знаю вас немного лучше. Это пригодится в нашем общении '
               f'{SYMS.smile}\nТеперь введите ваши контакты, и мы перейдем к основной части '
               f'{SYMS.rocket}\nУкажите номер телефона или email {SYMS.down}',
            en=f'Great, now I know you a little better. This will be useful in our communication '
               f'{SYMS.smile}\nNow enter your contacts and we will move on to the main part '
               f'{SYMS.rocket}\nPlease provide a phone number or email {SYMS.down}',
        )

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        try:
            if (num_role := await utils.data_to_str_digits(data=update.text)) \
                    and 1 <= int(num_role) <= len(settings.COMPANY_ROLES):
                user.role_in_company = settings.COMPANY_ROLES[int(num_role)]
            else:
                user.role_in_company = update.text
            await user.asave()

            add_reply_text = I18N(
                ru='О, думаю, это очень интересно',
                en='Oh, I think this is very interesting',
                common_right=SYMS.wonder + '\n\n'
            )

        except Exception as exc:
            self.log(message=exc, level='error')
            add_reply_text = I18N(
                ru='Не удалось сохранить роль в компании',
                en='Failed to save role in company',
                style='bold',
                common_left=SYMS.warning,
                common_right='\n\n',
            )
        return add_reply_text + self.reply_text, self.next_state

    def _set_messages(self) -> Dict:
        messages = [MessageGetContacts(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageGetAboutCommand(BaseMessage, Utils):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_about_command'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_role_in_company

    def _set_reply_text(self) -> Union[str, I18N]:
        reply_text = I18N(
            ru='Теперь укажите вашу роль в компании. Просто введите номер',
            en='Now indicate your role in the company. Just enter the number',
            common_right=':\n\n'
        )
        for num, role in settings.COMPANY_ROLES.items():
            reply_text += f'{num}. {role}\n'

        reply_text += I18N(
            ru='Если нет подходящего варианта — впишите вашу роль в поле для ответа',
            en='If there is no suitable option, enter your role in the answer field',
            common_left='\n'
        )
        return reply_text

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        try:
            user.company.about_team = update.text
            await user.company.asave()
            add_reply_text = I18N(
                ru='Информация о команде сохранена',
                en='Team information saved',
                style='bold',
                common_left=SYMS.bot_face,
                common_right='\n\n',
            )

        except Exception as exc:
            self.log(message=exc, level='error')

            add_reply_text = I18N(
                ru='Не удалось сохранить информацию о команде',
                en='Failed to save command information',
                style='bold',
                common_left=SYMS.warning,
                common_right='\n\n',
            )
        return add_reply_text + self.reply_text, self.next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetRoleInCompany()]}


class MessageGetAboutCompany(BaseMessage, Utils):
    """Сообщение при изменении информации о компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_about_company'

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_about_command

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru=f'Какая у вас команда? Опишите в свободной форме (сколько человек, '
               f'профессиональный и управленческий уровень членов команды и т.п.). Если есть '
               f'выраженная неоднородность в команде (например, разные поколения), тоже напишите,'
               f' это может быть важно',
            en="What is your team? Describe in free form (how many people, professional and "
               "managerial level of team members, etc.). If there is significant heterogeneity in"
               " the team (for example, different generations), write also, this may be important",
            style='bold',
            common_right='\n\n'
        )

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        try:
            user.company.about_company = update.text
            await user.company.asave()

            add_reply_text = I18N(
                ru='Информация о компании сохранена',
                en='Company information saved',
                style='bold',
                common_left=SYMS.bot_face,
                common_right='\n\n',
            )

        except Exception as exc:
            self.log(message=exc, level='error')
            add_reply_text = I18N(
                ru='Не удалось сохранить информацию о компании',
                en='Failed to save company information',
                style='bold',
                common_left=SYMS.warning,
                common_right='\n\n',
            )
        return add_reply_text + self.reply_text, self.next_state

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message for message in [MessageGetAboutCommand()]}


class MessageGetCompany(BaseMessage, Utils):
    """Сообщение при запросе от нового пользователя название компании"""
    message_get_about_company = [MessageGetAboutCompany()]
    message_get_role_in_company = [MessageGetRoleInCompany()]

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_company'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.reset_state
        user = update.user
        reply_text = I18N(
            ru='Ошибка регистрации компании',
            en='Company registration error',
            common_left=SYMS.warning
        )

        try:
            company, fact_create = await Company.objects.aget_or_create(name=update.text)
            user.company = company
            await user.asave()

            if company and fact_create:
                reply_text = I18N(
                    ru=f'Компания "{company.name}" успешно зарегистрирована\n\n'
                       f'Опишите вашу компанию (ниша, размер и тп)',
                    en=f'Company "{company.name}" has been successfully registered\n\n'
                       f'Describe your company (niche, size, etc.)',
                    common_left=SYMS.bot_face,
                    style='bold'
                )
                next_state = FSMGreetingScriptStates.get_about_company
                self.children_messages = {
                    message.state_or_key: message for message in self.message_get_about_company
                }
            elif company and not fact_create:
                reply_text = I18N(
                    ru=f'Компания "{company.name}" ранее зарегистрирована, Вы добавлены в список'
                       f' участников\n\nВведите номер, соответствующий Вашей роли в компании '
                       f'согласно пунктам или введите текстом свой вариант',
                    en=f'The company "{company.name}" was previously registered, you have been '
                       f'added to the list of participants\n\nEnter the number corresponding to'
                       f' your role in the company according to the points or '
                       f'enter your option in text',
                    style='bold',
                    common_left=SYMS.bot_face,
                    common_right=':\n\n'
                )
                for num, role in settings.COMPANY_ROLES.items():
                    reply_text += f'{num}. {role}\n'

                next_state = FSMGreetingScriptStates.get_role_in_company
                self.children_messages = {
                    message.state_or_key: message for message in self.message_get_role_in_company
                }
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class MessageGetFullname(BaseMessage, Utils):
    """Сообщение при старте знакомства с новым пользователем"""
    message_get_company = [MessageGetCompany()]
    message_get_role_in_company = [MessageGetRoleInCompany()]

    def _set_state_or_key(self) -> str:
        return 'FSMGreetingScriptStates:get_fullname'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        reply_text = I18N(
            ru='Введите название Вашей компании?',
            en='Enter your company name?',
            style='bold'
        )
        next_state = FSMGreetingScriptStates.get_company
        self.children_messages = {
            message.state_or_key: message for message in self.message_get_company
        }

        add_reply_text = I18N(
            ru='Не удалось сохранить имя и фамилию',
            en='Failed to save name and surname',
            style='bold',
            common_right='\n\n',
            common_left=SYMS.warning
        )
        try:
            name, surname, patronymic = utils.get_fullname(update.text)
            # изменён порядок на имя, фамилию отчество
            user.name = name
            user.surname = surname
            user.patronymic = patronymic
            await user.asave()

            add_reply_text = I18N(
                ru='Спасибо, я запомню',
                en="Thank you, I'll remember",
                common_left=SYMS.bot_face,
                common_right=SYMS.smile + '\n\n'
            )

            if user.company:
                reply_text = I18N(
                    ru=f'Очень приятно! {SYMS.smile_eyes}\nТеперь укажите вашу роль в компании. '
                       f'Просто введите номер',
                    en=f'Very nice! {SYMS.smile_eyes}\nNow indicate your role in the company. '
                       f'Just enter the number',
                    common_right=':\n\n'
                )

                for num, role in settings.COMPANY_ROLES.items():
                    reply_text += f'{num}. {role}\n'

                reply_text += I18N(
                    ru='Если нет подходящего варианта — впишите вашу роль в поле для ответа',
                    en='If there is no suitable option, enter your role in the answer field',
                    common_left='\n'
                )

                next_state = FSMGreetingScriptStates.get_role_in_company
                self.children_messages = {
                    message.state_or_key: message for message in self.message_get_role_in_company
                }
        except Exception as exc:
            self.log(message=exc, level='error')
        return add_reply_text + reply_text, next_state


class StartGreetingButton(BaseButton):
    """Класс описывающий кнопку - Познакомится"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Познакомится',
            en='Get acquainted',
        )

    def _set_next_state(self) -> str:
        return FSMGreetingScriptStates.get_fullname

    def _set_reply_text(self) -> Union[str, I18N]:
        reply_text = I18N(
            ru=f'Давайте знакомиться {SYMS.wink}\nРасскажите о себе. Есть ли у вас команда, '
               'компания, как там идут дела, какие у вас цели? Чем больше я о вас знаю, тем '
               'более точечную помощь смогу оказать.\nЯ — надежный собеседник и никому не выдам'
               f' ваши ответы. Мне интереснее обдумывать их самостоятельно {SYMS.smile}\n'
               'Давайте начнем с имени. Напишите, как вас зовут — Имя, Фамилия',
            en=f"Let's get acquainted {SYMS.wink}\nTell us about yourself. Do you have a team, "
               "a company, how are things going there, what are your goals? The more I know "
               "about you, the more targeted help I can provide.\nI am a reliable interlocutor "
               "and will not reveal your answers to anyone. It's more interesting for me to think"
               f" about them on my own {SYMS.smile}\nLet's start with the name. "
               "Write your name - Name, Surname",
            common_left=f'\n\n\n{SYMS.bot_face}'
        )
        return DEFAULT_GREETING + reply_text

    def _set_messages(self) -> Dict:
        return {message.state_or_key: message
                for message in [MessageGetFullname(parent_name=self.class_name)]}
