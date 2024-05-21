from asgiref.sync import async_to_sync
from django.db import models
from django.utils.translation import gettext_lazy as _

from telegram_bot.loader import bot
from .base_model import BaseModel


class Feedback(BaseModel):
    """Модель для хранения отзывов и предложений"""
    user = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='feedbacks',
        verbose_name=_('user'))

    feedback = models.TextField(null=False, blank=False, verbose_name=_('feedback'))

    response = models.TextField(null=True, blank=True, verbose_name=_('response'))

    admin = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='response_feedbacks',
        verbose_name=_('admin'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('feedback')
        verbose_name_plural = _('feedbacks')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.admin and self.response and self.is_active:
            async_to_sync(bot.send_message)(
                chat_id=self.user.tg_accounts.first().tg_user_id, text=self.response
            )
            self.is_active = False
            self.save()

    def __repr__(self):
        """Переопределение __repr__, для отображения названия объекта."""
        return f"Feedback id:{self.pk} | User:{self.user}"

    def __str__(self):
        """Переопределение __str__, для отображения названия объекта."""
        return f"Feedback id:{self.pk} | User:{self.user}"
