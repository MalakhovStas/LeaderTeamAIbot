"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from .models import SevenPetals
from users.models import User


class UserInline(admin.TabularInline):
    # readonly_fields = ('total',)
    readonly_fields = ('pk', 'username', 'surname', 'name', 'patronymic')
    fieldsets = (
        ('personal information', {'fields': ('pk', 'username', 'surname', 'name', 'patronymic')}),)
    model = User


@admin.register(SevenPetals)
class SevenPetalsAdmin(admin.ModelAdmin):
    """Регистрация модели SevenPetals в админке"""
    # fieldsets = (
    #     ('personal information', {'fields': ('__user',)}),)
    inlines = [UserInline]
    ordering = ('added_date',)
