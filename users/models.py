from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .manager import CustomUserManager
from company.models import Company


class User(AbstractUser):
    """Абстрактная модель User, добавляет в стандартную модель дополнительные поля."""

    username = models.CharField(
        max_length=256, unique=True, verbose_name=_('username'))

    name = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_('name'))

    surname = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_('surname'))

    patronymic = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_('patronymic'))

    phone_number = PhoneNumberField(
        unique=False, null=True, blank=True, verbose_name=_('phone number'))

    email = models.EmailField(null=True, blank=True, verbose_name=_('email'))

    photo = models.ImageField(
        upload_to='users_foto/', null=True, blank=True, verbose_name=_('photo'))

    company = models.ForeignKey(
        to=Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='members',
        verbose_name=_('company'))
    role_in_company = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_('role in company'))

    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = '-is_superuser', '-date_joined', '-is_active'

    def __repr__(self):
        """Переопределение __repr__, для отображения email в названии объекта."""
        return self.username

    def __str__(self):
        """Переопределение __str__, для отображения email в названии объекта."""
        return self.username
