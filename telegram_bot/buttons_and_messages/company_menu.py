"""Модуль формирования меню - личный кабинет"""
from typing import List, Optional, Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from django.conf import settings

from company.models import Company
from core.utils.i18n import I18N
from utils import utils
from .base_classes import Utils, BaseButton, BaseMessage, GoToBack
from .calendar_menu import CompanyCalendarButton
from ..config import SYMS
from ..utils.states import FSMCompanyMenuStates


class MessageChangeAboutTeam(BaseMessage, Utils):
    """Сообщение при изменении информации о команде"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:change_about_team'

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить информацию о команде',
            en='Failed to change command information',
            style='bold',
            common_left=SYMS.warning,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            user.company.about_team = update.text
            await user.company.asave()

            reply_text = I18N(
                ru=f'Звучит перспективно {SYMS.wink} Так и записываю',
                en=f"Sounds promising {SYMS.wink} So I’m writing it down",
            )
            next_state = self.reset_state
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangeAboutTeam(BaseButton, Utils):
    """Кнопка изменить информацию о команде"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Изменить информацию о команде',
            en='Change team information',
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Расскажите мне о вашей команде',
            en='Failed to change company information',
            common_left=SYMS.bot_face,
            common_right=SYMS.smile,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.change_about_team

    def _set_messages(self) -> Dict:
        messages = [MessageChangeAboutTeam(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageChangeAboutCompany(BaseMessage, Utils):
    """Сообщение при изменении информации о компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:change_about_company'

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить информацию о компании',
            en='Failed to change company information',
            style='bold',
            common_left=SYMS.warning,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            user.company.about_company = update.text
            await user.company.asave()

            reply_text = I18N(
                ru='Я запомню. Успехов на новом месте',
                en="I'll memorise. Good luck in your new place",
                common_right=SYMS.smile_eyes,
            )

            next_state = self.reset_state
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangeAboutCompany(BaseButton, Utils):
    """Кнопка изменить информацию о компании"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Изменить информацию о компании',
            en='Change company information',
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Расскажите мне о вашей компании',
            en='Tell me about your company',
            common_left=SYMS.bot_face,
            common_right=SYMS.smile,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.change_about_company

    def _set_messages(self) -> Dict:
        messages = [MessageChangeAboutCompany(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageChangeRoleInCompany(BaseMessage, Utils):
    """Сообщение при изменении роли в компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:change_role'

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось изменить роль в компании',
            en='Failed to change company role',
            style='bold',
            common_left=SYMS.warning,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            if (num_role := await utils.data_to_str_digits(data=update.text)) \
                    and 1 <= int(num_role) <= len(settings.COMPANY_ROLES):
                user.role_in_company = settings.COMPANY_ROLES[int(num_role)]
            else:
                user.role_in_company = update.text
            await user.asave()

            reply_text = I18N(
                ru='Я запомню. Успехов на новом месте',
                en="I'll memorise. Good luck in your new place",
                common_right=SYMS.smile_eyes,
            )
            next_state = self.reset_state
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class ChangeRoleInCompany(BaseButton, Utils):
    """Кнопка изменить роль в компании"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Изменить роль в компании',
            en='Change your role in the company',
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        reply_text = I18N(
            ru=f'Ого, вы взяли на себя что-то новенькое {SYMS.smile_eyes}\n'
               f'Введите номер, который соответствует вашей текущей роли',
            en=f"Wow, you've taken on something new {SYMS.smile_eyes}\n"
               f"Enter the number that matches your current role",
            common_left=SYMS.bot_face,
            common_right=':\n\n',
        )

        # TODO настроить перевод ролей в компании
        for num, role in settings.COMPANY_ROLES.items():
            reply_text += f'{num}. {role}\n'

        reply_text += I18N(
            ru='Если нет подходящего варианта — впишите вашу роль в поле для ответа',
            en='If there is no suitable option, enter your role in the answer field',
            common_left='\n',
        )
        return reply_text

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.change_role

    def _set_messages(self) -> Dict:
        messages = [MessageChangeRoleInCompany(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class MessageRegisterCompany(BaseMessage, Utils):
    """Сообщение при регистрации компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:register_company'

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Не удалось зарегистрировать компанию',
            en='Failed to register company',
            common_left=SYMS.warning,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user
        try:
            company, fact_create = await Company.objects.aget_or_create(name=update.text)

            if company and fact_create:
                user.company = company
                await user.asave()
                next_state = self.reset_state

                reply_text = I18N(
                    ru=f'Компания {company.name} успешно зарегистрирована, '
                       f'Вы добавлены в список участников',
                    en=f'Company {company.name} has been successfully registered, '
                       f'you have been added to the list of participants',
                    style='bold',
                )
            elif company and not fact_create:
                user.company = company
                await user.asave()
                next_state = self.reset_state

                reply_text = I18N(
                    ru=f'Компания {company.name} ранее зарегистрирована, '
                       f'Вы добавлены в список участников',
                    en=f'Company {company.name} was previously registered, '
                       f'you have been added to the list of participants',
                    style='bold',
                )
            else:
                reply_text = I18N(
                    ru='Ошибка регистрации компании',
                    en='Company registration error',
                    style='bold',
                )

        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class RegisterCompany(BaseButton, Utils):
    """Кнопка Регистрация компании"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Регистрация компании',
            en='Company registration',
        )

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите название компании',
            en='Enter company name',
            style='bold',
            common_left=SYMS.bot_face,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.register_company

    def _set_messages(self) -> Dict:
        messages = [MessageRegisterCompany(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class AddedCompanyMemberButton(BaseButton):
    """Класс описывающий кнопку - Пригласить участника команды"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(
            ru='Пригласить участника команды',
            en='Invite a team member',
            common_left=SYMS.woman_up_hand,
            common_right=SYMS.men_up_hand,
        )

    def _set_next_state(self) -> str:
        return self.reset_state

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text = I18N(
            ru='Это ссылка приглашение',
            en='This is an invitation link',
            common_left=SYMS.bot_face,
            common_right=SYMS.post_mail + '\n\n',
        )

        reply_text += utils.create_invite_link(
            bot_username=(await self.bot.get_me()).username, referrer_id=update.from_user.id)

        reply_text += I18N(
            ru=f'Отправьте ее вашему коллеге или партнеру. Он или она кликнет по ссылке и '
               f'попадет ко мне. А я впишу нового человека в вашу команду {SYMS.smile}\n\n'
               f'Внимание: ссылка действует только {settings.INVITE_LINK_LIFE // 60} минут',
            en=f'Send it to your colleague or partner. He or she will click on the link and '
               f'be taken to me. And I’ll add a new person to your team {SYMS.smile}\n\n'
               f'Attention: the link is only valid for {settings.INVITE_LINK_LIFE // 60} minutes',
            common_left='\n\n',
        )
        return reply_text, self.next_state


class CompanyMenu(BaseButton):
    """Класс описывающий кнопку - Компания"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Моя команда', en='My team', common_left=SYMS.command)

    def _set_next_state(self) -> str:
        return self.reset_state

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user

        if not user.company:
            reply_text = I18N(
                ru='Информация о компании не указана',
                en='Company information not provided',
                style='bold',
                common_left=SYMS.bot_face,
                common_right='\n\n',
            )
            self.children_buttons = [RegisterCompany(parent_name=self.class_name)]

        else:
            self.children_buttons = self._set_children()
            reply_text = I18N(
                ru='Команда компании',
                en='Team company',
                common_left=SYMS.bot_face,
                common_right=f' - {user.company.name}\n\n',
                general_style='bold'
            )

            reply_text += I18N(
                ru='Ваша роль в компании',
                en='Your role in the company',
                style='bold_italic',
                common_right=f": {user.role_in_company if user.role_in_company else ''}\n\n",
            )

            reply_text += I18N(
                ru='О компании',
                en='About company',
                style='bold_italic',
                common_right=f": {user.company.about_company if user.company.about_company else ''}\n\n",
            )

            reply_text += I18N(
                ru='О команде',
                en='About the team',
                style='bold_italic',
                common_right=f": {user.company.about_team if user.company.about_team else ''}\n\n",
            )

            reply_text += I18N(
                ru='Участники команды',
                en='Team members',
                style='bold_italic',
                common_right=f":\n",
            )

            num = 0
            async for member in user.company.members.all():
                num += 1
                # TODO настроить перевод ролей в компании
                reply_text += (
                    f"{SYMS.tab}{num}. {member.role_in_company} - "
                    f"{'Вы' if member == user else member.username}\n")
                # f"{I18N(ru='Вы', en='You') if member == user else member.username}\n")

            reply_text += I18N(
                ru='Откорректируйте, если у вас что-то поменялось',
                en='Please correct if anything has changed',
                common_left='\n',
                common_right=SYMS.down,
            )

        return reply_text, self.next_state

    def _set_children(self) -> List:
        return [
            CompanyCalendarButton(parent_name=self.class_name),
            AddedCompanyMemberButton(parent_name=self.class_name),
            ChangeRoleInCompany(parent_name=self.class_name),
            ChangeAboutCompany(parent_name=self.class_name),
            ChangeAboutTeam(parent_name=self.class_name),
        ]
