"""Модуль формирования меню - личный кабинет"""
from typing import List, Optional, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from users.models import User
from ..config import FACE_BOT, COMPANY_ROLES, INVITE_LINK_LIFE
from .base_classes import Utils, BaseButton, BaseMessage, GoToBack
from ..utils.states import FSMCompanyMenuStates
from company.models import Company
from utils import utils
from ..utils.misc_utils import create_invite_link


class MessageChangeAboutTeam(BaseMessage, Utils):
    """Сообщение при изменении информации о команде"""
    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:change_about_team'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Не удалось изменить информацию о команде</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
            user.company.about_team = update.text
            await user.company.asave()
            reply_text = f"<b>Информация о команде {user.company.name} успешно изменена</b>"
            next_state = 'reset_state'
        except Exception:
            pass
        return reply_text, next_state


class ChangeAboutTeam(BaseButton, Utils):
    """Кнопка изменить информацию о команде"""
    def _set_name(self) -> str:
        return 'Изменить информацию о команде'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Введите информацию команде:</b>\n'

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

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Не удалось изменить информацию о компании</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
            user.company.about_company = update.text
            await user.company.asave()
            reply_text = f"<b>Информация о компании {user.company.name} успешно изменена</b>"
            next_state = 'reset_state'
        except Exception:
            pass
        return reply_text, next_state


class ChangeAboutCompany(BaseButton, Utils):
    """Кнопка изменить информацию о компании"""
    def _set_name(self) -> str:
        return 'Изменить информацию о компании'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Введите информацию компании:</b>\n'

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

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Не удалось изменить роль в компании</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(
                tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
            if (num_role := await utils.data_to_str_digits(data=update.text)) \
                    and 1 <= int(num_role) <= len(COMPANY_ROLES):
                user.role_in_company = COMPANY_ROLES[int(num_role)]
            else:
                user.role_in_company = update.text
            await user.asave()
            reply_text = f"<b>Ваша роль в компании {user.company.name} успешно изменена</b>"
            next_state = 'reset_state'
        except Exception:
            pass
        return reply_text, next_state


class ChangeRoleInCompany(BaseButton, Utils):
    """Кнопка изменить роль в компании"""
    def _set_name(self) -> str:
        return 'Изменить роль в компании'

    def _set_reply_text(self) -> Optional[str]:
        reply_text = FACE_BOT + ('<b>Введите номер, соответствующий Вашей роли в компании '
                                 'согласно пунктам или введите текстом свой вариант:</b>\n\n')
        for num, role in COMPANY_ROLES.items():
            reply_text += f'{num}. {role}\n'
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

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Не удалось зарегистрировать компанию</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            user = await User.objects.filter(tg_accounts__tg_user_id=update.from_user.id).afirst()
            company, fact_create = await Company.objects.aget_or_create(name=update.text)
            if company and fact_create:
                user.company = company
                await user.asave()
                reply_text = (f"<b>Компания {company.name} успешно зарегистрирована, "
                              f"Вы добавлены в список участников</b>")
                next_state = 'reset_state'
            elif company and not fact_create:
                user.company = company
                await user.asave()
                reply_text = (f"<b>Компания {company.name} ранее зарегистрирована, "
                              f"Вы добавлены в список участников</b>")
                next_state = 'reset_state'
            else:
                reply_text = "<b>Ошибка регистрации компании</b>"
        except Exception:
            pass
        return reply_text, next_state


class RegisterCompany(BaseButton, Utils):
    """Кнопка регистрация компании"""
    def _set_name(self) -> str:
        return 'Регистрация компании'

    def _set_reply_text(self) -> Optional[str]:
        return FACE_BOT + '<b>Введите название компании</b>'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.register_company

    def _set_messages(self) -> Dict:
        messages = [MessageRegisterCompany(parent_name=self.class_name)]
        return {message.state_or_key: message for message in messages}


class CompanyCalendarButton(BaseButton):
    """Класс описывающий кнопку - Календарь команды"""

    def _set_name(self) -> str:
        return '📆 \t Календарь команды'

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = await User.objects.filter(
            tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
        reply_text = f'<b>{FACE_BOT} Календарь команды, компании "{user.company.name}"</b>\n\n'
        reply_text += user.company.calendar or 'нет данных'
        return reply_text, self.next_state


class AddedCompanyMemberButton(BaseButton):
    """Класс описывающий кнопку - Добавить члена команды"""

    def _set_name(self) -> str:
        return '🤵 \t Добавить члена команды'

    def _set_next_state(self) -> str:
        return 'reset_state'

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        from ..loader import bot
        reply_text = (f'{FACE_BOT} <b>Ссылка-приглашение</b>\n\n'
                      f'Отправьте эту ссылку новому члену команды, при переходе он будет '
                      f'автоматически добавлен в Вашу команду\n\n'
                      f'⚠ Время действия ссылки - {INVITE_LINK_LIFE // 60} минут\n\n')
        reply_text += create_invite_link(
            bot_username=(await bot.get_me()).username, referrer_id=update.from_user.id)
        return reply_text, self.next_state


class CompanyMenu(BaseButton):
    """Класс описывающий кнопку - Компания"""

    def _set_name(self) -> str:
        return '🏢 \t Компания'

    def _set_next_state(self) -> str:
        return 'reset_state'

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = await User.objects.filter(
            tg_accounts__tg_user_id=update.from_user.id).select_related("company").afirst()
        if not user.company:
            reply_text = f"<b>{FACE_BOT}Информация о компании не указана</b>\n\n"
            self.children_buttons = [RegisterCompany(parent_name=self.class_name)]

        else:
            self.children_buttons = self._set_children()
            # from asgiref.sync import sync_to_async
            # company_members = await sync_to_async(list)(user.company.members.all())
            # company_members = [member async for member in user.company.members.all()]
            # for num, member in enumerate(user.company.members.all(), 1):

            reply_text = f'<b>{FACE_BOT} Компания "{user.company.name}"</b>\n\n'
            # reply_text += (f"<b>Название:</b> "
            #                f"{user.company.name if user.company.name else ''}\n")
            reply_text += (f"<b>Ваша роль в компании:</b> "
                           f"{user.role_in_company if user.role_in_company else ''}\n\n")
            reply_text += (f"<b>О компании:</b> "
                           f"{user.company.about_company if user.company.about_company else ''}\n\n")
            reply_text += (f"<b>О команде:</b> "
                           f"{user.company.about_team if user.company.about_team else ''}\n\n")
            reply_text += f"<b>Участники:</b>\n"
            num = 0
            async for member in user.company.members.all():
                num += 1
                reply_text += (f"{num}. {member.role_in_company} - "
                               f"{'Вы' if member == user else member.username}\n")
        return reply_text, self.next_state

    def _set_children(self) -> List:
        return [
            # CompanyCalendarButton(parent_name=self.class_name),
            AddedCompanyMemberButton(parent_name=self.class_name),
            ChangeRoleInCompany(parent_name=self.class_name),
            ChangeAboutCompany(parent_name=self.class_name),
            ChangeAboutTeam(parent_name=self.class_name),
        ]
