"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from .models import TelegramAccount


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    """Регистрация модели TelegramAccount в админке"""
    ordering = ('created_at',)
    fields = (
        'user',
        'tg_user_id',
        'tg_username',
        'tg_first_name',
        'tg_last_name',
        'access',
        'position',
        'text_last_request',
        'created_at',
        'updated_at'
    )
    readonly_fields = 'created_at', 'updated_at'

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
