"""Модуль конфигурации логирования"""
from loguru import logger
from django.conf import settings


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    # 'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            # 'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


LOGS_DIR = settings.BASE_DIR.joinpath('logs')

DEBUG_FORMAT = ("{time:DD-MM-YYYY at HH:mm:ss} | {level} | file: {file} "
                "| func: {function} | line: {line} | message: {message}")

ERRORS_FORMAT = "{time:DD-MM-YYYY at HH:mm:ss} | {level} | {file} | {message}"
SECURITY_FORMAT = "{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}"

logger_common_args = {
    "diagnose": True,
    "backtrace": False,
    "rotation": settings.LOGS_ROTATION,
    "retention": settings.LOGS_RETENTION,
    "compression": "zip",
}

logger.add(**{
    "sink": LOGS_DIR.joinpath("debug.log"),
    "level": "DEBUG",
    "format": DEBUG_FORMAT,
    **logger_common_args
})

logger.add(**{
    "sink": LOGS_DIR.joinpath("errors.log"),
    "level": "WARNING",
    "format": ERRORS_FORMAT,
    **logger_common_args
})

logger.add(**{
    "sink": LOGS_DIR.joinpath("RequestsManager.log"),
    "level": "DEBUG",
    "format": DEBUG_FORMAT,
    "filter": lambda msg: msg.get("message").startswith('RequestsManager'),
    **logger_common_args
})
