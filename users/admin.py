from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from psychological_testing.models import SevenPetals
from telegram_bot.models import TelegramAccount
from .models import User
from django.urls import reverse

AdminSite.site_header = settings.PYPROJECT['tool']['poetry']['name']


class TelegramAccountInline(admin.StackedInline):
    model = TelegramAccount
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    verbose_name = _('telegram account')
    verbose_name_plural = ''
    fieldsets = [(None, {'fields': ()})]


@admin.register(User)
class UserRegAdmin(UserAdmin):
    """Регистрация модели User в админке"""

    inlines = [TelegramAccountInline]
    readonly_fields = (
        'user_last_seven_petals',
        'ai_dialog',
        'date_joined',
        'updated_at',
        'last_login',
        'display_photo',
        'display_graph_seven_petals',
        'display_graph_seven_petals_statistics',
        'personal_data_processing_agreement',
    )
    ordering = '-is_superuser', '-is_staff', '-username',
    search_fields = ('username',)

    def get_fieldsets(self, request, obj=None):
        credentials = (_('credentials'), {'classes': ('collapse',), 'fields': ('password',)})
        permissions = (_('permissions'), {'classes': ('collapse',), 'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )})
        communication_assistant = (_('communication with the assistant'),
                                   {'classes': ('collapse',), 'fields': ('ai_dialog',)})
        fieldsets = [
            (_('important dates'),
             {'fields': (
                 'date_joined',
                 'updated_at',
                 'last_login'
             )}),
            (_('personal information'),
             {'fields': (
                 'display_photo',
                 'personal_data_processing_agreement',
                 'username',
                 'name',
                 'surname',
                 'patronymic',
                 'language',
                 'phone_number',
                 'email',
                 'company',
             )}),
            (_('psychological testing'),
             {'fields': (
                    'user_last_seven_petals',
                    'display_graph_seven_petals',
                    'display_graph_seven_petals_statistics',
             )}),
        ]
        if request.user.is_superuser:
            if obj is None:
                credentials = (_('credentials'), {
                    'classes': ('wide',), 'fields': ('password1', 'password2')
                })
            fieldsets.insert(0, credentials)
            fieldsets.insert(1, permissions)
        if obj and obj.ai_dialog:
            fieldsets.append(communication_assistant)
        return fieldsets

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def display_photo(self, obj):
        """Отображение фотографии пользователя"""
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="100" height="100" />')
        else:
            return mark_safe(f'<img src="/static/no_image.png" width="100" height="100" />')

    display_photo.allow_tags = True
    display_photo.short_description = _('photo')

    def get_user_last_seven_petals(self, obj):
        """Возвращает объект последнего тестирования seven_petals пользователя"""
        if obj.pk:
            return SevenPetals.objects.filter(user=obj).first()

    def user_last_seven_petals(self, obj):
        """Отображает последнее тестирование seven_petals пользователя"""
        result = '-'
        if obj.pk and (last_seven_petals := self.get_user_last_seven_petals(obj)):
            url = reverse(
                viewname=f'admin:{last_seven_petals._meta.app_label}_'
                         f'{last_seven_petals._meta.model_name}_change',
                args=[last_seven_petals.pk]
            )
            result = format_html(f'<a href="{url}">{last_seven_petals}</a>')
        return result

    def display_graph_seven_petals_statistics(self, obj):
        """Отображение графика статистики тестирования пользователя"""
        # FIXME убрать хард код

        result = '-'
        if obj.pk:
            filename = f'users_tests_graphs/tg_user_id:{obj.pk}_seven_petals_statistics.png'
            result = mark_safe(
                f'<img src="{settings.MEDIA_URL}{filename}" width="340" height="500"/>'
            )
        return result

    display_graph_seven_petals_statistics.allow_tags = True
    display_graph_seven_petals_statistics.short_description = _('graph statistics')

    def display_graph_seven_petals(self, obj):
        """Отображение графика тестирования пользователя"""
        if obj.pk and (last_seven_petals := self.get_user_last_seven_petals(obj)):
            return mark_safe(
                f'<img src="{last_seven_petals.graph.url}" width="320" height="240" />')
        return "-"

    display_graph_seven_petals.allow_tags = True
    display_graph_seven_petals.short_description = _('graph')
