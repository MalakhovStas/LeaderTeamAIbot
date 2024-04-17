"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from users.models import User
from .models import Company, CalendarEvent, CalendarEventReminder


# @admin.register(CalendarEventReminder)
# class CalendarEventReminderAdmin(admin.ModelAdmin):
#     pass


class CalendarEventReminderInline(admin.TabularInline):
    """Отображение модели CalendarEventReminder"""
    model = CalendarEventReminder
    extra = 0
    readonly_fields = ('reminder_date',)
    verbose_name_plural = _('reminders')


@admin.register(CalendarEvent)
class CalendarEventsAdmin(admin.ModelAdmin):
    """Регистрация модели CalendarEvent в админке"""
    inlines = [CalendarEventReminderInline]


class ActiveCalendarEventInline(admin.TabularInline):
    """Отображение модели CalendarEvent - активных событий"""
    model = CalendarEvent
    extra = 0
    classes = ('collapse',)
    show_change_link = True
    verbose_name_plural = _('calendar - active events')

    def get_queryset(self, request):
        """Получение активных событий"""
        return self.model.objects.filter(is_active=True).all()


class PastCalendarEventInline(admin.TabularInline):
    """Отображение модели CalendarEvent - прошедших событий"""
    model = CalendarEvent
    extra = 0
    max_num = 0
    classes = ('collapse',)
    readonly_fields = (
        'title',
        'event_date',
        'description',
    )
    # show_change_link = True
    verbose_name_plural = _('calendar - past events')

    def get_queryset(self, request):
        """Получение прошедших событий"""
        return self.model.objects.filter(is_active=False).all()


class CompanyUserInline(admin.TabularInline):
    """Отображение модели User"""
    model = User
    fields = (
        'username_with_link',
        'name',
        'surname',
        'patronymic',
        'role_in_company',
        'email',
        'phone_number',
        'seven_petals'
    )
    readonly_fields = (
        'role_in_company',
        'username_with_link',
        'name',
        'surname',
        'patronymic',
        'phone_number',
        'email',
        'seven_petals'
    )
    extra = 0
    max_num = 0
    can_delete = False
    classes = ('collapse',)
    verbose_name_plural = _('command')
    exclude = ('pk',)

    def username_with_link(self, obj):
        """Отображает username пользователя со ссылкой для перехода"""
        result = '-'
        if obj.pk:
            url = reverse(
                viewname=f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
                args=[obj.pk]
            )
            result = format_html(f'<a href="{url}">{obj.username}</a>')
        return result

    username_with_link.short_description = _('username')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Регистрация модели Company в админке"""
    inlines = [CompanyUserInline, ActiveCalendarEventInline, PastCalendarEventInline]
    ordering = ('created_at',)
    readonly_fields = (
        'seven_petals',
        'display_graph',
        'num_calendar_active_events',
        'num_calendar_past_events'
    )
    search_fields = ('name',)

    @staticmethod
    def display_graph(obj):
        """Отображение графика тестирования"""
        if obj.seven_petals and obj.seven_petals.graph:
            return mark_safe(
                f'<img src="{obj.seven_petals.graph.url}" width="320" height="240" />')
        return "-"

    display_graph.allow_tags = True
    display_graph.short_description = _('graph')

    @staticmethod
    def num_calendar_active_events(obj):
        """Отображение количества активных событий календаря"""
        if obj.calendar_active_events:
            return len(obj.calendar_active_events)
        return "-"
    num_calendar_active_events.short_description = _('number of active calendar events')

    @staticmethod
    def num_calendar_past_events(obj):
        """Отображение количества прошедших событий календаря"""
        if obj.calendar_past_events:
            return len(obj.calendar_past_events)
        return "-"

    num_calendar_active_events.short_description = _('number of past calendar events')
