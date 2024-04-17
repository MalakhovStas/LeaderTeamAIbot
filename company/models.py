"""Модуль формирования моделей БД Телеграм аккаунтов"""
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from config.models.base_model import BaseModel
from psychological_testing.models import SevenPetals
from .managers.calendar_events_manager import CalendarEventManager


class Company(BaseModel):
    """Модель хранения данных о компании"""
    name = models.CharField(unique=True, max_length=512, verbose_name=_('company name'))
    phone_number = PhoneNumberField(
        unique=False, null=True, blank=True, verbose_name=_('phone number'))
    about_company = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name=_('about company'))
    about_team = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name=_('about team'))

    seven_petals = models.OneToOneField(
        to=SevenPetals,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='company',
        verbose_name=_('seven_petals'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['-created_at']

    @property
    def calendar_active_events(self) -> QuerySet:
        """Динамически получает, активные события календаря"""
        return self.calendar_events.filter(active_event=True).all()

    @property
    def calendar_past_events(self) -> QuerySet:
        """Динамически получает, прошедшие события календаря"""
        return self.calendar_events.filter(active_event=False).all()

    def save(self, *args, **kwargs):
        """Переопределение метода save для перерасчёта данных тестирования компании,
        при сохранении, учитывая только тех пользователей которые прошли тестирование """
        super().save(*args, **kwargs)
        if not self.seven_petals:
            self.seven_petals = SevenPetals()
        else:
            self.seven_petals.optimism = 0
            self.seven_petals.stream = 0
            self.seven_petals.sense = 0
            self.seven_petals.love = 0
            self.seven_petals.play = 0
            self.seven_petals.study = 0
            self.seven_petals.impact = 0
            self.seven_petals.general_questions = 0

        if members := [user for user in self.members.all() if user.seven_petals]:
            eff = 1 / len(members)

            for user in members:
                self.seven_petals.optimism += (user.seven_petals.optimism * eff)
                self.seven_petals.stream += (user.seven_petals.stream * eff)
                self.seven_petals.sense += (user.seven_petals.sense * eff)
                self.seven_petals.love += (user.seven_petals.love * eff)
                self.seven_petals.play += (user.seven_petals.play * eff)
                self.seven_petals.study += (user.seven_petals.study * eff)
                self.seven_petals.impact += (user.seven_petals.impact * eff)
                self.seven_petals.general_questions += (user.seven_petals.general_questions * eff)
        self.seven_petals.save()

    def __repr__(self):
        """Переопределение __repr__, для отображения company name в названии объекта."""
        return f"company name: {self.name}"

    def __str__(self):
        """Переопределение __str__, для отображения company name в названии объекта."""
        return f"company name: {self.name}"


class CalendarEvent(BaseModel):
    """Модель хранения данных о событии календаря компании"""

    objects = CalendarEventManager()

    title = models.CharField(max_length=1024, verbose_name=_('title'))
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name=_('company')
    )
    event_date = models.DateTimeField(verbose_name=_('event date'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('calendar event')
        verbose_name_plural = _('calendar events')
        ordering = ['event_date']

    def __repr__(self):
        """Переопределение __repr__, для отображения данных события в названии объекта."""
        return f"event_date: {self.event_date} | title: {self.title}"

    def __str__(self):
        """Переопределение __str__, для отображения данных события в названии объекта."""
        return f"event_date: {self.event_date} | title: {self.title}"


class CalendarEventReminder(BaseModel):
    """Модель хранения данных о напоминании о событии календаря компании"""

    INTERVAL_CHOICES = [
        (timezone.timedelta(days=7), _('week')),
        (timezone.timedelta(days=3), _('three days')),
        (timezone.timedelta(days=1), _('one day')),
        (timezone.timedelta(hours=12), _('twelve hours')),
        (timezone.timedelta(hours=6), _('six hours')),
        (timezone.timedelta(hours=3), _('three hours')),
        (timezone.timedelta(hours=1), _('one hour')),
        (timezone.timedelta(minutes=30), _('thirty minutes')),
        (timezone.timedelta(minutes=15), _('fifteen minutes')),
        (timezone.timedelta(minutes=10), _('ten minutes')),
        (timezone.timedelta(minutes=5), _('five minutes')),
        (timezone.timedelta(minutes=3), _('three minutes')),
        (timezone.timedelta(minutes=1), _('one minute')),
    ]

    interval = models.DurationField(choices=INTERVAL_CHOICES)
    reminder_date = models.DateTimeField(null=True, blank=True, verbose_name=_('reminder date'))
    event = models.ForeignKey(
        CalendarEvent,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name=_('event')
    )

    def save(self, *args, **kwargs):
        """Переопределение метода save для сохранения напоминаний только в будущем времени"""
        if not self.pk:
            self.reminder_date = self.event.event_date - self.interval
            if self.reminder_date > timezone.now():
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
