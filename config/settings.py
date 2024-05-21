"""
Django settings for BlankDjangoAiogramTgBot project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import json
import os
from pathlib import Path

import django.conf
from corsheaders.defaults import default_headers
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from pytoml import parser  # type: ignore
from redis import StrictRedis

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
DEVELOPER = "https://github.com/MalakhovStas"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f*^g0bh-(vwb(y)bf&qpq2%+3nwmj3loboc6jnco(m#dnu0k26'

# Словарь с данными проекта из pyproject.toml
with open('pyproject.toml', 'r') as file:
    PYPROJECT = parser.load(file)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR.joinpath('env/.env.default'), override=True)
load_dotenv(dotenv_path=BASE_DIR.joinpath('env/.env.local'), override=True)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['194.58.96.166', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = []
PROJECT_IN_DEV = True
ADMINS_ACCESS_ONLY = False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_results',
    'django_celery_beat',
    'celery_progress',
    'corsheaders',
    'django_jinja',
    'phonenumber_field',
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    'company.apps.CompanyConfig',
    'psychological_testing.apps.PsychologicalTestingConfig',
    'telegram_bot.apps.TelegramBotConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Данные о компании
COMPANY_PHONES = [
    (_('Collection department'), '+7-495-777-77-77'),
    (_('Contact department'), '+7-495-777-77-77'),
    (_('Legal service'), '+7-495-777-77-77'),
]
COMPANY_EMAIL = ('E-mail', 'example@mail.ru')
COMPANY_ADDRESS = (_('Address'), _('Moscow, st.Moskovskaya.77'))
COMPANY_WORKING_HOURS = (_('Working time'), _('weekdays from 10:00 to 19:00'))

# Вспомогательные тексты
LOGIC_IN_DEV = _('Functionality of this block is under development')

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [Path(BASE_DIR).joinpath("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            # django-jinja defaults
            "match_extension": ".j2",
            "match_regex": None,
            "app_dirname": "templates",

            # Can be set to "jinja2.Undefined" or any other subclass.
            "undefined": None,
            "newstyle_gettext": True,
            "tests": {
                # "mytest": "path.to.my.test",
            },
            "filters": {
                'myi18n': django
                # "myfilter": "path.to.my.filter",
            },
            "globals": {
                # "myglobal": "path.to.my.globalfunc",
            },
            "constants": {
                'company_phones': COMPANY_PHONES,
                'company_email': COMPANY_EMAIL,
                'company_address': COMPANY_ADDRESS,
                'company_working_hours': COMPANY_WORKING_HOURS,
                'logic_in_dev': LOGIC_IN_DEV,
                'settings': django.conf.settings
            },
            "policies": {
                "ext.i18n.trimmed": True,
            },

            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.i18n",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.DebugExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "django_jinja.builtins.extensions.DjangoExtraFiltersExtension",
            ],

            "bytecode_cache": {
                "name": "default",
                "backend": "django_jinja.cache.BytecodeCache",
                "enabled": False,
            },

            "autoescape": True,
            "auto_reload": DEBUG,
            "translation_engine": "django.utils.translation",

            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],

        }
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],

        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASE_DATA: dict = json.loads(
    os.getenv("DATABASE_DEV", default={}) if PROJECT_IN_DEV else os.getenv("DATABASE", default={})
)
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE_DATA.get('db'),
        'USER': DATABASE_DATA.get('user'),
        'PASSWORD': DATABASE_DATA.get('password'),
        'HOST': DATABASE_DATA.get('host'),
        'PORT': DATABASE_DATA.get('port'),
    }
}

CACHE_DATA: dict = json.loads(
    os.getenv("CACHE_DEV", default={}) if PROJECT_IN_DEV else os.getenv("CACHE", default={})
)

REDIS_CACHE = StrictRedis(
    host=CACHE_DATA.get('host'),
    port=int(CACHE_DATA.get('port')),
    db=int(CACHE_DATA.get('db')),
    decode_responses=True,
    charset="utf-8",
)

REDIS_URL = f"redis://{CACHE_DATA.get('host')}:{CACHE_DATA.get('port')}/{CACHE_DATA.get('db')}"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
    # STATIC_ROOT = STATICFILES_DIRS
else:
    if PROJECT_IN_DEV:
        STATIC_ROOT = '/home/Development/static/'
    else:
        STATIC_ROOT = '/home/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = ["127.0.0.1"]

AUTH_USER_MODEL = 'users.User'

FIXTURE_DIRS = [BASE_DIR / 'fixtures']

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Данные для отправки сообщений на почту пользователя.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'unsafe-none'
CORS_ALLOW_ALL_ORIGINS = True  # Добавляет заголовок "Access-Control-Allow-Headers: * "
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['OPTIONS', 'GET', 'POST']
CORS_ALLOW_HEADERS = list(default_headers) + [
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Credentials",
    "accept",
    "accept-encoding",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "X-Amz-Date"
]

# Настройки RequestsManager
REQUESTS_TIMEOUT = 60
MAX_REQUEST_RETRIES = 2
DEFAULT_CONTENT_TYPE = 'application/json'

# Настройки логирования
# при достижении *.log файла указанного размера -> файл сжимается в *.log.zip
LOGS_ROTATION = "10 mb"
# количество сжатых файлов для хранения, не более
LOGS_RETENTION = 1

# Настройки Celery
# Вывод логов сelery_workers в консоль
STDOUT_STDERR_WORKERS_TO_CONSOLE = True
# Интервал запуска задачи в секундах
TASK_INTERVAL = 60
# максимальный уровень приоритетов
X_MAX_PRIORITY = 10

APP_CONFIG = {'periodic_tasks_workers': []}

GENERAL_DATETIME_FORMAT_FOR_MESSAGE = "%d.%m.%Y %H:%M"

# Ниже настройки Телеграмм бота

# Количество перезапусков бота в случае падения
MAX_RESTART_BOT = 3

# Токен и имя телеграм бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NIKNAME = os.getenv('BOT_NIKNAME')

# Список администраторов и ссылка на чат поддержки и менеджера
ADMINS = os.getenv('ADMINS').split(', ') if os.getenv('ADMINS') else tuple()
TECH_ADMINS = os.getenv('TECH_ADMINS').split(', ') if os.getenv('TECH_ADMINS') else tuple()
# SUPPORT = f"tg://openmessage?user_id={os.getenv('SUPPORT_ID')}"
SUPPORT = f"https://t.me/{os.getenv('SUPPORT_USERNAME')}"
# CONTACT_MANAGER = f"tg://openmessage?user_id={os.getenv('CONTACT_MANAGER_ID')}"
CONTACT_MANAGER = f"https://t.me/{os.getenv('CONTACT_MANAGER_USERNAME')}"

# Команды бота
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    # ('profile', 'Настройки профиля'),
    # ('chatgpt', 'Пообщаться с AI'),
)

# Файл информации о пользователях по команде admin
PATH_USERS_INFO = 'users_info.xlsx'

# Включение / отключение механизма защиты от флуда
FLOOD_CONTROL = True

# Время между сообщениями от пользователя для защиты от флуда в секундах
FLOOD_CONTROL_TIME = 0.3

# Количество предупреждений перед блокировкой для защиты от флуда
FLOOD_CONTROL_NUM_ALERTS = 10

# Время остановки обслуживания пользователя для защиты от флуда в секундах
FLOOD_CONTROL_STOP_TIME = 60

# Время жизни реферальной ссылки для добавления пользователей в секундах
INVITE_LINK_LIFE = 60*60

# Настройки дефолтного timeout для aiohttp запросов RequestsManager
RM_TIMEOUT = 20

# Настройка планировщика задач apscheduler, время между запуском
# AutoUpdateFeedbackManager -> finding_unanswered_feedbacks - интервал обновления отзывов
AUFM_INTERVAL_SECONDS = 60*60  # каждый час

# Настройки прокси
USE_PROXI = True
PROXI_FILE = BASE_DIR.joinpath('proxy.txt')
TYPE_PROXI = 'SOCKS5'

# Доступное кол-во запросов по умолчанию
DEFAULT_FREE_BALANCE_REQUEST_USER = 1_000_000

# Пароли пользователей по умолчанию
DEFAULT_ADMIN_PASSWORD = "admin"
DEFAULT_USER_PASSWORD = "user_password"

# Роли в компаниях
COMPANY_ROLES = {
    1: 'Собственник бизнеса',
    2: 'СЕО',
    3: 'Топ-менеджер',
    4: 'Руководитель подразделения',
    5: 'HR',
    6: 'Специалист',
}

# переназначает переменные, используется в продакшн
from . import production_settings  # noqa F401,E402