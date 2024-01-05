"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from .models import TelegramAccount


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    """Регистрация модели TelegramAccount в админке"""
    ordering = ('added_date',)
