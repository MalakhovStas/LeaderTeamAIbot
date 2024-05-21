"""Модуль формирования меню - календарь"""
from typing import List, Optional, Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from django.conf import settings

from company.models import CalendarEvent
from company.models import CalendarEventReminder
from core.utils.i18n import I18N
from utils import utils
from .base_classes import Utils, BaseButton, BaseMessage, GoToBack
from ..config import SYMS
from ..utils.states import FSMCompanyMenuStates


class MessageAddCalendarEventDate(BaseMessage, Utils):
    """Сообщение при создании события календаря компании, добавление даты события"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:add_calendar_event_date'

    def _set_next_state(self) -> Optional[str]:
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Ошибка, не удалось сохранить событие, введена некорректная дата',
            en='Error, event could not be saved, incorrect date entered',
            common_left=SYMS.warning,
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user

        try:
            data = await state.get_data()
            title = data.pop('new_calendar_event_title', None)
            description = data.pop('new_calendar_event_description', None)
            await state.set_data(data)

            if ((date := utils.data_to_datetime(update.text))
                    and title and description and user.company):
                event = await CalendarEvent.objects.acreate(
                    title=title,
                    description=description,
                    event_date=date,
                    company=user.company)

                reply_text = I18N(
                    ru='Новое событие календаря успешно сохранено',
                    en='New calendar event saved successfully',
                    common_left=SYMS.bot_face
                )

                # TODO сделать перевод сообщений каждому пользователю на основе его настроек языка
                async for member in user.company.members.all():
                    async for tg_account in member.tg_accounts.all():
                        await self.bot.send_message(
                            chat_id=tg_account.tg_user_id,
                            text=f'В календарь компании добавлено новое событие\n\n'
                                 f'<i>Название</i>: <b>{event.title}</b>\n'
                                 f'<i>Описание</i>: {event.description}\n'
                                 f'<i>Дата</i>: {event.event_date.strftime(settings.GENERAL_DATETIME_FORMAT_FOR_MESSAGE)}\n'
                        )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class MessageAddCalendarEventDescription(BaseMessage, Utils):
    """Сообщение при создании события календаря компании, добавление описания события"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:add_calendar_event_description'

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.add_calendar_event_date

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите дату события в формате',
            en='Enter the event date in the format',
            common_left=SYMS.bot_face,
            common_right=':\n01/01/2024 12:00',
            common_style='bold',
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            await state.update_data({'new_calendar_event_description': update.text})
        except Exception as exc:
            self.log(message=exc)
        return reply_text, next_state


class MessageAddCalendarEventTitle(BaseMessage, Utils):
    """Сообщение при создании события календаря компании, добавление названия события"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:add_calendar_event_title'

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.add_calendar_event_description

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Ошибка, некорректные данные - название события не может быть пустым',
            en='Error, incorrect data - event name cannot be empty',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            if update.text:
                await state.update_data({'new_calendar_event_title': update.text})
                reply_text = I18N(
                    ru=f'Введите описание для этого события',
                    en='Enter a description for this event',
                    common_left=SYMS.bot_face,
                )
            else:
                self.next_state = self.reset_state
        except Exception as exc:
            self.log(message=exc)
        return reply_text, next_state


class AddCalendarEventButton(BaseButton, Utils):
    """Кнопка добавить событие календаря компании"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Добавить событие', en='Add an event')

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите название события',
            en='Enter event name',
            common_left=SYMS.bot_face
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.add_calendar_event_title

    def _set_messages(self) -> Dict:
        messages = [
            MessageAddCalendarEventTitle(parent_name=self.class_name),
            MessageAddCalendarEventDescription(parent_name=self.class_name),
            MessageAddCalendarEventDate(parent_name=self.class_name)
        ]
        return {message.state_or_key: message for message in messages}


class MessageDeleteCalendarEvent(BaseMessage, Utils):
    """Сообщение при удалении события календаря компании"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:delete_calendar_event'

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.add_calendar_event_description

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Ошибка, не удалось удалить событие, возможно не верно введён Id',
            en='Error, the event could not be deleted, the Id may have been entered incorrectly',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        try:
            event_id = int(await utils.data_to_str_digits(update.text))
            if event_id:
                delete_info = await CalendarEvent.objects.filter(pk=event_id).adelete()
                if delete_info[0]:
                    reply_text = I18N(
                        ru=f'Событие календаря Id: {event_id} успешно удалено',
                        en='Calendar event Id: {event_id} successfully deleted',
                        common_left=SYMS.bot_face,
                    )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class DeleteCalendarEventButton(BaseButton, Utils):
    """Кнопка удалить событие календаря компании"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Удалить событие', en='Delete event')

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите Id события',
            en='Enter event Id',
            common_left=SYMS.bot_face
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.delete_calendar_event

    def _set_messages(self) -> Dict:
        messages = [
            MessageDeleteCalendarEvent(parent_name=self.class_name),
        ]
        return {message.state_or_key: message for message in messages}


class MessageAddReminderCalendarEventInterval(BaseMessage, Utils):
    """Сообщение при добавлении напоминания к событию календаря компании, выбор интервала"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:add_reminder_calendar_event_interval'

    def _set_next_state(self) -> Optional[str]:
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Ошибка, не удалось добавить напоминание к событию,'
               ' возможно не верно введён номер интервала до события',
            en='Error, it was not possible to add a reminder to the event,'
               ' the number of the interval before the event may have been entered incorrectly',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        reply_text = self.reply_text
        try:
            data = await state.get_data()
            event_id = data.pop('new_calendar_event_reminder_event_id', None)
            await state.set_data(data)
            num = int(await utils.data_to_str_digits(update.text)) - 1

            if (event_id and 0 <= num <= len(CalendarEventReminder.INTERVAL_CHOICES)
                    and (interval := CalendarEventReminder.INTERVAL_CHOICES[num][0])):

                new_reminder = await CalendarEventReminder.objects.acreate(
                    interval=interval,
                    event=await CalendarEvent.objects.aget(pk=event_id)
                )

                if not new_reminder.pk:
                    reply_text = I18N(
                        ru='Нельзя создать напоминание в прошедшем времени',
                        en='You cannot create a reminder in the past tense',
                        common_left=SYMS.warning,
                    )
                else:
                    reply_text = I18N(
                        ru=f'Напоминание к событию Id: {event_id} успешно сохранено',
                        en=f'Reminder for event Id: {event_id} successfully saved',
                        common_left=SYMS.bot_face,
                    )
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, self.next_state


class MessageAddReminderCalendarEventId(BaseMessage, Utils):
    """Сообщение при добавлении напоминания к событию календаря компании, выбор события"""

    def _set_state_or_key(self) -> str:
        return 'FSMCompanyMenuStates:add_reminder_calendar_event_id'

    def _set_next_state(self) -> Optional[str]:
        return self.reset_state

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Ошибка, не удалось добавить напоминание к событию, возможно не верно введён Id',
            en='Error, it was not possible to add a reminder to the event, '
               'the Id may have been entered incorrectly',
            common_left=SYMS.warning
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        next_state = self.next_state
        reply_text = self.reply_text
        user = update.user

        try:
            if ((event_id := int(await utils.data_to_str_digits(update.text))) and event_id in [
                event.pk async for event in user.company.calendar_active_events]):

                await state.update_data({'new_calendar_event_reminder_event_id': event_id})

                reply_text = I18N(
                    ru='Введите номер интервала напоминания до события',
                    en='Enter the reminder interval number before the event',
                    common_left=SYMS.bot_face,
                    common_right=':\n\n'
                )

                for num, (key, value) in enumerate(CalendarEventReminder.INTERVAL_CHOICES, 1):
                    reply_text += f'{num}. {value.capitalize()}\n'

                next_state = FSMCompanyMenuStates.add_reminder_calendar_event_interval
        except Exception as exc:
            self.log(message=exc, level='error')
        return reply_text, next_state


class AddReminderCalendarEventButton(BaseButton, Utils):
    """Кнопка добавить напоминание к событию календаря компании"""

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Добавить напоминание к событию', en='Add a reminder to an event')

    def _set_reply_text(self) -> Union[str, I18N]:
        return I18N(
            ru='Введите Id события',
            en='Enter event Id',
            style='bold',
            common_left=SYMS.bot_face
        )

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    def _set_next_state(self) -> Optional[str]:
        return FSMCompanyMenuStates.add_reminder_calendar_event_id

    def _set_messages(self) -> Dict:
        messages = [
            MessageAddReminderCalendarEventId(parent_name=self.class_name),
            MessageAddReminderCalendarEventInterval(parent_name=self.class_name),
        ]
        return {message.state_or_key: message for message in messages}


class CompanyCalendarButton(BaseButton):
    """Класс описывающий кнопку - Календарь команды"""
    add_event_button = AddCalendarEventButton(parent_name="CompanyCalendarButton")
    delete_event_button = DeleteCalendarEventButton(parent_name="CompanyCalendarButton")
    add_reminder_event_button = AddReminderCalendarEventButton(parent_name="CompanyCalendarButton")

    def _set_name(self) -> Union[str, I18N]:
        return I18N(ru='Календарь команды', en='Team calendar', common_left=SYMS.calendar)

    def _set_next_state(self) -> str:
        return self.reset_state

    def _set_children(self) -> List:
        return [GoToBack(new=False)]

    async def _set_answer_logic(self, update: Message, state: Optional[FSMContext] = None):
        user = update.user
        owner = utils.get_key_from_value_dict(settings.COMPANY_ROLES, user.role_in_company) == 1

        reply_text = I18N(
            ru='Календарь команды, компании',
            en='Calendar of the team, company',
            common_right=f' - {user.company.name}\n\n',
            general_style='bold',

        )

        async for event in user.company.calendar_active_events:
            if owner:
                reply_text += I18N(
                    ru='Id',
                    en='Id',
                    style='bold_italic',
                    common_right=f': {event.pk}\n',
                )

            reply_text += I18N(
                ru='Событие',
                en='Event',
                style='bold_italic',
                common_right=f': {event.title}\n',

            )
            reply_text += I18N(
                ru='Описание',
                en='Description',
                style='bold_italic',
                common_right=f': {event.description}\n',

            )
            reply_text += I18N(
                ru='Дата',
                en='Date',
                style='bold_italic',
                common_right=f': ' + event.event_date.astimezone().strftime(
                    settings.GENERAL_DATETIME_FORMAT_FOR_MESSAGE),

            )
            if owner:
                reply_text += I18N(
                    ru='Напоминания',
                    en='Reminders',
                    style='bold',
                    common_left='\n\n',
                    common_right=f':\n',

                )
                choices = dict(CalendarEventReminder.INTERVAL_CHOICES)
                async for reminder in event.reminders.filter(is_active=True).all():
                    # TODO настроить перевод интервалов напоминания
                    reply_text += f'    {choices[reminder.interval]}\n'

            reply_text += '\n\n'
        if owner:
            if self.add_event_button not in self.children_buttons:
                self.children_buttons.insert(0, self.add_event_button)
            if self.delete_event_button not in self.children_buttons:
                self.children_buttons.insert(1, self.delete_event_button)
            if self.add_reminder_event_button not in self.children_buttons:
                self.children_buttons.insert(2, self.add_reminder_event_button)
        return SYMS.bot_face + reply_text, self.next_state
