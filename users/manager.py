from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from asgiref.sync import sync_to_async, async_to_sync


class CustomUserManager(BaseUserManager):
    """Менеджер модели User"""

    @sync_to_async
    def create_user(self, username, password, **extra_fields):
        """Добавление пользователя"""
        if not username:
            raise ValueError(_('Username not specified'))
        # email = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    @async_to_sync
    async def create_superuser(self, username, password, **extra_fields):
        """Добавление суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('The superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('The superuser must have is_superuser=True.'))
        return await self.create_user(username, password, **extra_fields)
