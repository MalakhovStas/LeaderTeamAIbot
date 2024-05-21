"""Модуль реализации логики рассылки уведомлений о событии календаря компании членам команды"""

from django.conf import settings
from django.utils import timezone

from company.models import CalendarEvent
from company.models import CalendarEventReminder
from telegram_bot.config import SYMS
from telegram_bot.loader import bot
from users.models import User


# TODO всё работает нужно  нормально настроить


async def send_calendar_event_reminder_from_reminder():
    """Рассылка уведомлений о событии календаря компании членам команды из CalendarEventReminder"""
    reminders = CalendarEventReminder.objects.filter(
        is_active=True).select_related("event__company").all()

    async for reminder in reminders:
        if reminder.reminder_date <= timezone.now():
            async for member in reminder.event.company.members.all():
                # FIXME добавить перевод
                async for tg_account in member.tg_accounts.all():
                    await bot.send_message(
                        chat_id=tg_account.tg_user_id,
                        text=f'{SYMS.bot_face} Через {dict(CalendarEventReminder.INTERVAL_CHOICES)[reminder.interval]} - {reminder.event.event_date.astimezone().strftime(settings.GENERAL_DATETIME_FORMAT_FOR_MESSAGE)}\nсостоится событие: <b>"{reminder.event.title}"</b>\n{reminder.event.description}'
                    )
            reminder.is_active = False
            await reminder.asave()


async def send_calendar_event_reminder_from_user(user: User, event: CalendarEvent):
    """Рассылка уведомлений о создании события календаря компании членам команды из User"""
    # FIXME не используется из-за circular imports код лежит в telegram_bot/buttons_and_messages/calendar_menu.py стр:55
    async for member in user.company.members.all():
        async for tg_account in member.tg_accounts.all():
            await bot.send_message(
                chat_id=tg_account.tg_user_id,
                text=f'В календарь компании добавлено новое событие\n\n'
                     f'<i>Название</i>: <b>{event.title}</b>\n'
                     f'<i>Описание</i>: {event.description}\n'
                     f'<i>Дата</i>: {event.event_date.strftime(settings.GENERAL_DATETIME_FORMAT_FOR_MESSAGE)}\n'
            )
