from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from telegram_bot.models import TelegramAccount
from .models import User

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
        'seven_petals',
        'ai_dialog',
        'date_joined',
        'updated_at',
        'last_login',
        'display_photo',
        'display_graph',
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
                 'username',
                 'name',
                 'surname',
                 'patronymic',
                 'phone_number',
                 'email',
                 'company',
             )}),
            (_('psychological testing'),
             {'fields': (
                 'seven_petals',
                 'display_graph',

             )}),
        ]
        if request.user.is_superuser:
            if obj is None:
                credentials = (_('credentials'), {
                    'classes': ('wide',), 'fields': ('password1', 'password2')
                })
            fieldsets.insert(0, credentials)
            fieldsets.insert(1, permissions)
        if obj.ai_dialog:
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

    def display_graph(self, obj):
        """Отображение графика тестирования"""
        if obj.seven_petals and obj.seven_petals.graph:
            return mark_safe(
                f'<img src="{obj.seven_petals.graph.url}" width="320" height="240" />')
        return "-"

    display_graph.allow_tags = True
    display_graph.short_description = _('graph')
