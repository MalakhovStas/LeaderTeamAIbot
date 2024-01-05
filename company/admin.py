"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Регистрация модели Company в админке"""
    ordering = ('added_date',)
