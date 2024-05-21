from django.db import models
from .base_model import BaseModel
from django.utils.translation import gettext_lazy as _


class AssistantSettings(BaseModel):
    """Модель для хранения настроек ИИ ассистента"""
    openai_api_key = models.CharField(
        max_length=1024, null=False, blank=False, verbose_name='openai api key'
    )
    openai_organization = models.CharField(
        max_length=1024, null=False, blank=False, verbose_name='openai organization'
    )
    proxy_url = models.CharField(
        max_length=256, null=True, blank=True, verbose_name='proxy url'
    )
    model = models.CharField(
        max_length=256, null=False, blank=True, default='gpt-3.5-turbo', verbose_name='model'
    )
    temperature = models.FloatField(
        null=False, blank=True, default=0.8, verbose_name='temperature'
    )
    max_tokens = models.IntegerField(
        null=False, blank=True, default=2048, verbose_name='max tokens'
    )
    top_p = models.FloatField(
        null=False, blank=True, default=1.0, verbose_name='top_p'
    )
    presence_penalty = models.FloatField(
        null=False, blank=True, default=1.0, verbose_name='presence penalty'
    )
    frequency_penalty = models.FloatField(
        null=False, blank=True, default=0.1, verbose_name='frequency penalty'
    )
    timeout = models.IntegerField(
        null=False, blank=True, default=45, verbose_name='timeout'
    )
    invitation = models.TextField(
        null=False, blank=True, default='', verbose_name=_('invitation')
    )
    base_prompt = models.TextField(
        null=False, blank=True, default='', verbose_name=_('base prompt')
    )
    recommendations_prompt = models.TextField(
        null=False, blank=True, default='', verbose_name=_('recommendations prompt')
    )

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('assistant config')
        ordering = ['-created_at']

    def __repr__(self):
        """Переопределение __repr__, для отображения названия объекта."""
        return f"AI Assistant settings id:{self.pk}"

    def __str__(self):
        """Переопределение __str__, для отображения названия объекта."""
        return f"AI Assistant settings id:{self.pk}"
