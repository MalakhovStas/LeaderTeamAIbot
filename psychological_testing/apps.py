from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PsychologicalTestingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'psychological_testing'
    verbose_name = _('psychological testing')
    verbose_name_plural = _('psychological tests')
