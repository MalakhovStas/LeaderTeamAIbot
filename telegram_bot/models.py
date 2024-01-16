"""Модуль формирования моделей БД Телеграм аккаунтов"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from .config import DEFAULT_FREE_BALANCE_REQUEST_USER


class TelegramAccount(models.Model):
    """Модель хранения данных Телеграм аккаунта"""
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, null=True, blank=True,
                             related_name='tg_accounts', verbose_name=_('user'))

    tg_phone_number = PhoneNumberField(
        unique=False, null=True, blank=True, verbose_name=_('phone number'))

    tg_user_id = models.BigIntegerField(
        null=False, blank=False, verbose_name=_('telegram user_id'))

    tg_username = models.CharField(
        max_length=512, null=True, blank=True, verbose_name=_('telegram username'))

    tg_first_name = models.CharField(
        max_length=512, null=True, blank=True, verbose_name=_('telegram first_name'))

    tg_last_name = models.CharField(
        max_length=512, null=True, blank=True, verbose_name=_('telegram last_name'))

    # Телеграм id пользователя по чьей ссылке пришел этот пользователь
    referer_id = models.BigIntegerField(
        null=True, blank=True, verbose_name=_('referer_id'))

    # Режим доступа к боту
    access = models.CharField(
        null=False, blank=True, default="allowed", verbose_name=_('access'))

    # Время начала блокировки пользователя используется в middleware
    start_time_limited = models.IntegerField(
        null=True, blank=True, verbose_name=_('start time limited'))

    position = models.CharField(
        max_length=256, null=False, blank=True,
        default="user", verbose_name=_('position')
    )

    password = models.CharField(
        max_length=256, null=False, blank=True,
        default="default-password", verbose_name=_('password')
    )

    date_last_request = models.DateTimeField(
        auto_now=True, verbose_name=_('date last request'))
    text_last_request = models.CharField(
        max_length=256, null=False, blank=True, default="first start command",
        verbose_name=_('text last request')
    )
    num_requests = models.IntegerField(
        null=False, blank=True, default=1, verbose_name=_('num requests'))

    ban_from_user = models.BooleanField(
        null=False, blank=True, default=False, verbose_name=_('ban from user'))

    balance_requests = models.IntegerField(
        null=False,
        blank=True,
        default=DEFAULT_FREE_BALANCE_REQUEST_USER,
        verbose_name=_('balance requests')
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, null=False,
                                  blank=True, default=0, verbose_name=_('balance'))
    subscription = models.DateTimeField(null=True, blank=True, verbose_name=_('subscription'))

    added_date = models.DateTimeField(auto_now_add=True, verbose_name=_('added date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('telegram account')
        verbose_name_plural = _('telegram accounts')
        ordering = ['-added_date']

    def __repr__(self):
        """Переопределение __repr__, для отображения id и username в названии объекта."""
        return f"id: {self.tg_user_id} | tg_username: {self.tg_username}"

    def __str__(self):
        """Переопределение __str__, для отображения id и username в названии объекта."""
        return f"id: {self.tg_user_id} | tg_username: {self.tg_username}"
