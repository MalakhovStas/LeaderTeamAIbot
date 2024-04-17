"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from users.models import User
from .models import SevenPetals


class SevenPetalsUserInline(admin.StackedInline):
    model = User
    fieldsets = [(None, {'fields': ()})]
    can_delete = False
    show_change_link = True
    verbose_name_plural = ''

    class Media:
        """Изменение отображения класса"""
        css = {"all": ("admin/css/custom_admin.css",)}


@admin.register(SevenPetals)
class SevenPetalsAdmin(admin.ModelAdmin):
    """Регистрация модели SevenPetals в админке"""
    verbose_name = _('test seven petals')
    verbose_name_plural = _('test seven petals')
    inlines = [SevenPetalsUserInline]
    ordering = ('created_at',)
    readonly_fields = ('display_graph',)

    def display_graph(self, obj):
        """Отображение графика тестирования"""
        if obj and obj.graph:
            return mark_safe(f'<img src="{obj.graph.url}" width="640" height="480" />')
        return "-"

    display_graph.allow_tags = True
    display_graph.short_description = _('display graph')
