from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegAdmin(UserAdmin):
    """Регистрация модели User в админке"""

    list_display = 'username', 'is_superuser', 'is_staff', 'is_active',
    readonly_fields = ('seven_petals', 'ai_dialog',)
    fieldsets = (
        (_('credentials'), {'fields': ('username', 'password',)}),
        (_('personal information'),
         {'fields': (
             'name',
             'surname',
             'patronymic',
             'phone_number',
             'email',
             'photo',
             'company',
             'seven_petals',
             'ai_dialog',

         )}),
        # (
        #     _('permissions'),
        #     {
        #         'fields': (
        #             'is_active',
        #             'is_staff',
        #             'is_superuser',
        #             'groups',
        #             'user_permissions',
        #         ),
        #     },
        # ),
        # (_('important dates'), {'fields': ('last_login', 'date_joined',)}),
        (_('important dates'), {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2',),
            },
        ),
    )
    ordering = '-is_superuser', '-is_staff',
    search_fields = ('username',)


admin.site.register(User, UserRegAdmin)
AdminSite.site_header = settings.PYPROJECT['tool']['poetry']['name']
