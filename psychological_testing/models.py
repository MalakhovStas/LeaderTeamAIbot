"""Модуль формирования моделей БД психологического тестирования пользователя"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class SevenPetals(models.Model):
    """Модель хранения данных опроса 'Семь лепестков'"""

    optimism = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('optimism'))

    stream = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('stream'))

    sense = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('sense'))
    
    love = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('love'))

    play = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('play'))
    
    study = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('study'))
    
    impact = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('impact'))

    general_questions = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('general questions'))

    open_questions_pleasure = models.CharField(
        max_length=8192, null=True, blank=True, verbose_name=_('open questions pleasure'))

    open_questions_irritation = models.CharField(
        max_length=8192, null=True, blank=True, verbose_name=_('open questions irritation'))

    added_date = models.DateTimeField(auto_now_add=True, verbose_name=_('added date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('seven petals')
        verbose_name_plural = _('seven petals')
        ordering = ['-modification_date']

    def __repr__(self):
        """Переопределение __repr__, для отображения информации о тестировании"""
        return f"SevenPetals: id: {self.pk}, "

    def __str__(self):
        """Переопределение __repr__, для отображения информации о тестировании"""
        return f"SevenPetals: id: {self.pk}"
