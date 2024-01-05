"""Модуль формирования моделей БД Телеграм аккаунтов"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Company(models.Model):
    """Модель хранения данных о компании"""
    # user = models.ManyToManyField(
    #     to='users.User', blank=True, related_name='users', verbose_name=_('user'))
    # inn = models.IntegerField(unique=True, verbose_name=_('inn'))

    name = models.CharField(unique=True, max_length=512, verbose_name=_('company name'))

    phone_number = PhoneNumberField(
        unique=False, null=True, blank=True, verbose_name=_('phone number'))

    about_company = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name=_('about company'))

    about_team = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name=_('about team'))

    calendar = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name=_('calendar team'))

    added_date = models.DateTimeField(auto_now_add=True, verbose_name=_('added date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['-added_date']

    def __repr__(self):
        """Переопределение __repr__, для отображения company name в названии объекта."""
        return f"company name: {self.name}"

    def __str__(self):
        """Переопределение __str__, для отображения company name в названии объекта."""
        return f"company name: {self.name}"
