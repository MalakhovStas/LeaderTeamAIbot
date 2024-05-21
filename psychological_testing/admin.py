"""Модуль конфигурации админки моделей Телеграм бота"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from users.models import User
from .models import SevenPetals
from django.conf import settings


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
    # inlines = [SevenPetalsUserInline]
    ordering = ('created_at',)
    readonly_fields = (
        'display_graph',
        'user',
        'company',
        'display_test_subject',
        'display_graph_statistics'
    )
    fieldsets = [
        (_('Test results'),
         {'fields': (
             'optimism',
             'stream',
             'sense',
             'love',
             'play',
             'study',
             'impact',
             'general_questions',
             'open_questions_pleasure',
             'open_questions_irritation',
         )}),
        (_('Visual representation'),
         {'fields': (
             'graph',
             'display_graph',
             # 'display_graph_statistics',
             'ai_recommendations'
         )}),
        (_('Test subject'),
         {'fields': (
             'display_test_subject',
         )}),
    ]

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
    def display_test_subject(self, obj):
        """Отображение графика тестирования"""
        result = '-'
        if obj:
            if obj.user:
                url = reverse(
                    viewname=f'admin:{obj.user._meta.app_label}_{obj.user._meta.model_name}_change',
                    args=[obj.user.pk]
                )
                result = format_html(f'<a href="{url}">{obj.user}</a>')
            if obj.company:
                url = reverse(
                    viewname=f'admin:{obj.company._meta.app_label}_{obj.company._meta.model_name}_change',
                    args=[obj.company.pk]
                )
                result = format_html(f'<a href="{url}">{obj.company}</a>')
        return result

    display_test_subject.allow_tags = True
    display_test_subject.short_description = _('subject')

    def display_graph(self, obj):
        """Отображение графика тестирования"""
        if obj and obj.graph:
            return mark_safe(f'<img src="{obj.graph.url}" width="640" height="480"/>')
        return "-"

    display_graph.allow_tags = True
    display_graph.short_description = _('display graph')

    def display_graph_statistics(self, obj):
        """Отображение графика статистики тестирования пользователя"""
        # FIXME убрать хард код
        result = '-'
        if obj.pk:
            if obj.user:
                filename = f'users_tests_graphs/tg_user_id:{obj.user.pk}_seven_petals_statistics.png'
                result = mark_safe(
                    f'<img src="{settings.MEDIA_URL}{filename}" width="640" height="1000"/>'
                )
            if obj.company:
                filename = f'companies_tests_graphs/company_id:{obj.company.pk}_seven_petals_statistics.png'
                result = mark_safe(
                    f'<img src="{settings.MEDIA_URL}{filename}" width="640" height="1000"/>'
                )
        return result
    display_graph_statistics.allow_tags = True
    display_graph_statistics.short_description = _('graph statistics')
