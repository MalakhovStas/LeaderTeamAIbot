"""Модуль конфигурации Телеграм бота"""
import json
from pathlib import Path
from django.conf import settings


import os
from dotenv import load_dotenv
load_dotenv()


DEBUG = settings.DEBUG
TIME_ZONE = settings.TIME_ZONE

TG_BOT_BASE_DIR = Path(__file__).parent

""" Количество перезапусков бота в случае падения """
MAX_RESTART_BOT = 3

""" Токен и имя телеграм бота """
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NIKNAME = os.getenv('BOT_NIKNAME')
ADMINS = os.getenv('ADMINS')
TECH_ADMINS = os.getenv('TECH_ADMINS')
SUPPORT = os.getenv('SUPPORT')
FACE_BOT = '🤖 \t '

""" Список администраторов и ссылка на чат поддержки и менеджера"""
ADMINS = os.getenv('ADMINS').split(', ') if os.getenv('ADMINS') else tuple()
TECH_ADMINS = os.getenv('TECH_ADMINS').split(', ') if os.getenv('TECH_ADMINS') else tuple()
SUPPORT = f"https://t.me/{os.getenv('SUPPORT')}"
CONTACT_MANAGER = f"https://t.me/{os.getenv('CONTACT_MANAGER')}"

""" Команды бота """
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('profile', 'Настройки профиля'),
    # ('chatgpt', 'Пообщаться с AI'),
)

"""Настройки OpenAI"""
OpenAI_TOKEN = os.getenv('OPENAI_API_KEY')
OpenAI_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION')
MODEL = 'gpt-3.5-turbo'
TEMPERATURE = 0.8
MAX_TOKENS = 2048
TOP_P = 1
PRESENCE_PENALTY = 0
FREQUENCY_PENALTY = 0.1
TIMEOUT = 45
INVITATION = 'Напиши ответ:'

""" Ответы open_ai по умолчанию """
DEFAULT_FEED_ANSWER = ' \t Cгенерируйте ответ кнопкой\n \t "Сгенерировать ответ"\n\n' \
                      ' \t или введите ответ вручную по кнопке\n \t "Редактировать ответ"'
DEFAULT_NOT_ENOUGH_BALANCE = 'Ваш лимит запросов исчерпан, пожалуйста пополните баланс'

""" Файл информации о пользователях по команде admin """
PATH_USERS_INFO = 'users_info.xlsx'

""" Включение / отключение механизма защиты от флуда """
FLOOD_CONTROL = True

""" Время между сообщениями от пользователя для защиты от флуда в секундах """
FLOOD_CONTROL_TIME = 0.3

""" Количество предупреждений перед блокировкой для защиты от флуда"""
FLOOD_CONTROL_NUM_ALERTS = 10

""" Время остановки обслуживания пользователя для защиты от флуда в секундах """
FLOOD_CONTROL_STOP_TIME = 60

""" Время жизни реферальной ссылки для добавления пользователей в секундах """
INVITE_LINK_LIFE = 60*60

""" Настройки дефолтного timeout для aiohttp запросов RequestsManager """
RM_TIMEOUT = 20

""" Настройка планировщика задач apscheduler, время между запуском 
    AutoUpdateFeedbackManager -> finding_unanswered_feedbacks - интервал обновления отзывов """
AUFM_INTERVAL_SECONDS = 60*60  # каждый час
# AUFM_INTERVAL_SECONDS = 60

""" Настройки прокси """
USE_PROXI = True
PROXI_FILE = TG_BOT_BASE_DIR.joinpath('proxy.txt')
TYPE_PROXI = 'SOCKS5'

DEFAULT_FREE_BALANCE_REQUEST_USER = 100

DEFAULT_GREETING = f"""
{FACE_BOT} Привет! Я виртуальный ИИ Ассистент команды. 
Я здесь, чтобы помочь вам взглянуть на ваш стиль лидерства и вашу команду под новым углом и 
обеспечить вас всеми необходимыми инсайтами и аналитикой для принятия обоснованных решений. 
А еще я буду периодически напоминать вам о том, как компания “Счастье в деятельности” может 
помочь вам решить актуальные для вас задачи. Если вы захотите, я буду информировать вас о новых 
продуктах и услугах, а также приглашать на наши события. Ваш запрос - это начало нашего пути к 
обнаружению возможностей и получению ответов на сложные вопросы, о которых вы, возможно, раньше 
не задумывались. Если вы не знаете, что спросить - попросите меня задать вам вопросы, которые 
помогут сформулировать ваш запрос. Чем больше я узнаю о вас и ваших уникальных целях, задачах и
вызовах, тем точнее будут мои ответы и рекомендации. Для начала, расскажите немного про себя, 
свою компанию и команду. Чем вы занимаетесь, к какой отрасли относитесь, какая у вас команда?
Воспользуйтесь главным меню, чтобы ввести данные о себе и Вашей компании.
"""

COMPANY_ROLES = {
    1: 'Собственник бизнеса',
    2: 'СЕО',
    3: 'Топ-менеджер',
    4: 'Руководитель подразделения',
    5: 'HR',
    6: 'Специалист',
}
