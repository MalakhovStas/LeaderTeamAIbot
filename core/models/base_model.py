from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Базовая абстрактная модель"""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('creation date')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated date')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('active'))

    class Meta:
        abstract = True
