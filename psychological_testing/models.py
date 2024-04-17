"""Модуль формирования моделей БД психологического тестирования пользователя"""
import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from config.models.base_model import BaseModel


class SevenPetals(BaseModel):
    """Модель хранения данных опроса 'Семь лепестков'"""

    optimism = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('optimism'))

    stream = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('stream'))

    sense = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('sense'))

    love = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('love'))

    play = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('play'))

    study = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('study'))

    impact = models.FloatField(
        null=False, blank=True, default=0, verbose_name=_('impact'))

    general_questions = models.SmallIntegerField(
        null=False, blank=True, default=0, verbose_name=_('general questions'))

    open_questions_pleasure = models.CharField(
        max_length=8192, null=True, blank=True, verbose_name=_('open questions pleasure'))

    open_questions_irritation = models.CharField(
        max_length=8192, null=True, blank=True, verbose_name=_('open questions irritation'))

    graph = models.ImageField(
        upload_to='users_tests_graphs/', null=True, blank=True, verbose_name=_('graph'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('seven petals')
        verbose_name_plural = _('seven petals')
        ordering = ['-updated_at']

    def delete(self, *args, **kwargs):
        """Переопределение метода для удаления связанного файла"""
        if self.graph and os.path.isfile(self.graph.path):
            os.remove(self.graph.path)
        super().delete(*args, **kwargs)

    def __repr__(self):
        """Переопределение __repr__, для отображения информации о тестировании"""
        return f"SevenPetals: id: {self.pk}, "

    def __str__(self):
        """Переопределение __repr__, для отображения информации о тестировании"""
        return f"SevenPetals: id: {self.pk}"
