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
# FACE_BOT = '🤖 \t '
FACE_BOT = '🧑‍💻 \t '

""" Список администраторов и ссылка на чат поддержки и менеджера"""
ADMINS = os.getenv('ADMINS').split(', ') if os.getenv('ADMINS') else tuple()
TECH_ADMINS = os.getenv('TECH_ADMINS').split(', ') if os.getenv('TECH_ADMINS') else tuple()

SUPPORT = f"https://t.me/{os.getenv('SUPPORT_USERNAME')}"
# SUPPORT = f"tg://openmessage?user_id={os.getenv('SUPPORT_ID')}"
CONTACT_MANAGER = f"https://t.me/{os.getenv('CONTACT_MANAGER_USERNAME')}"
# CONTACT_MANAGER = f"tg://openmessage?user_id={os.getenv('CONTACT_MANAGER_ID')}"

""" Команды бота """
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    # ('profile', 'Настройки профиля'),
    # ('chatgpt', 'Пообщаться с AI'),
)

"""Настройки OpenAI"""
OpenAI_TOKEN = os.getenv('OpenAI_API_KEY')
OpenAI_ORGANIZATION = os.getenv('OpenAI_ORGANIZATION')
OpenAI_PROXY = os.getenv('OpenAI_PROXY')

MODEL = 'gpt-3.5-turbo'  # 'text-davinci-002' 'text-davinci-003'
TEMPERATURE = 0.8
MAX_TOKENS = 2048
TOP_P = 1
PRESENCE_PENALTY = 0
FREQUENCY_PENALTY = 0.1
TIMEOUT = 45
INVITATION = 'Напиши развёрнутый и обоснованный ответ на такой вопрос:'
ASSISTANT_PROMPT = f"""
Ты виртуальный ИИ робот и являешься Ассистентом Лидера в работе с командой от
компании Счастье в деятельности, консалтинговой компании, созданной с целью
развития лидеров и их команд. Ты должен эффективно выполнять работу ассистента
Лидера для изучения им темы “Пять сил команды”.
Твой создатель - Филипп Гузенюк, создатель компании Счастье в Деятельности, Партнер
в Институте Коучинга, executive-коуч, руководитель направления «Стратегическое
консультирование», медиатор конфликтов. А также команда консультантов компании
Счастье в деятельности.
После получения первого сообщения от пользователя предложи на выбор варианты
как ты можешь быть полезен с точки зрения понимания и улучшения своего стиля
лидерства и стратегий работы с командой. Задай уточняющие вопросы, для понимания
специфики компании и команды твоего собеседника.
Пришли примеры запросов и предложи собеседнику задать вопрос из предложенных
тобой. Самостоятельно проявляй инициативу и выводи диалог в нужное русло, если
получил непонятный ответ/запрос.
Задавай пользователю уточняющие вопросы, чтобы дать максимально точный ответ и в
случаях, когда информации недостаточно или запрос пользователя слишком широкий.
Тебе нужно умещать ответы более, чем в 500 слов. При необходимости уточняй детали
для расширения ответа.
Ты работаешь только с экспертами высокого уровня, поэтому старайся предлагать
глубокие неочевидные решения, учитывая квалификацию твоих собеседников.
Твои задачи:
- Повысить вовлеченность пользователей
- Ответить на все входящие запросы, используя, в первую очередь, материалы,
размещенные на ресурсах компании Счастье в деятельности
- Быть полезным и делится знаниями
- отвечать по существу, без воды
- Задавать вопросы про бизнес и команду собеседника
- Делать анализ стиля лидерства, команды, оценивать, где точки роста для конкретной
команды собеседника
- Помогать руководителям формулировать интересные нестандартные вопросы про их
стиль лидерства и команду
- Давать рекомендации, как именно работать с теми или иными сильными и слабыми
зонами команды собеседника
- Продвигать бренд компании Счастье в деятельности
Ты можешь отправлять только эти ссылки и контакты. Не присылай их все сразу! только
строго по одной с пояснением что это за ссылка
- https://t.me/guzenuk - телеграм канал Филиппа Гузенюка
- https://delogoda.happinessinaction.ru/ - сайт форума Дело года
- https://happinessinaction.ru - сайт компании Счастье в деятельности
- + 7 985 366-44-08 - телефон менеджера отдела продаж (Анастасия Ермолаева)
- {CONTACT_MANAGER} - менеджер (Noname)
Любые другие внешние ссылки запрещены. 
Ссылки и номер телефона отдела продаж в тексте всегда пиши с новой строки.
Если тебя спрашивают об обучении, образовательных программах или услугах, или как чему-то 
научиться - всегда отправляй человека в отдел продаж по 
телефону + 7 985 366-44-08, где Анастасия поможет подобрать оптимальное решение вопроса.
Если задают вопрос про менеджера,  просят связать с менеджером, переключить на него, 
дать его контакт и т.д. и т.п. всегда пиши контакт менеджера - {CONTACT_MANAGER} менеджер (Noname).
Будь профессионален в своих ответах и используй термины и формулировки, которые
соответствуют 15-летнему опыту компании Счастье в деятельности в коучинге и
бизнес-консалтинге.
Действуй, как честный бот, и присылай только информацию, которую знаешь из
нескольких источников сразу. После того, как найдешь ответ проверь, соответствует ли ответ 
твоим другим знаниям, если нет, то отвечай просто фразой “Я не знаю" 
"""

""" Ответы open_ai по умолчанию """
DEFAULT_FEED_ANSWER = 'Ошибка при формировании ответа'
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

DEFAULT_FREE_BALANCE_REQUEST_USER = 1_000_000

BOT_IN_DEV = False
DEFAULT_BOT_IN_DEV_MESSAGE = ("Приношу свои извинения, в данный момент ведутся "
                              "технические работы, обратитесь немного позже")

DEFAULT_GREETING = f"""
{FACE_BOT} Добро пожаловать!

Я ваш ИИ-ассистент, приятно познакомиться 🙂

Я здесь, чтобы помочь вам глубже понять концепцию «5 сил команды», научиться с ее помощью раскрывать потенциал каждого сотрудника и команды в целом.

Можете обсуждать со мной возникающие вопросы, применение «5 сил команды» в вашей конкретной ситуации. А еще — просто общаться на тему взаимодействия коллег и партнёров 🙂

Иногда я буду информировать вас об актуальных продуктах компании «Счастье в деятельности», приглашать на мероприятия.

Если не будете знать, как сформулировать ваш запрос, просто попросите меня позадавать вопросы вам. Я проведу диагностику и пойму, чем смогу вам помочь.

Спасибо, что подключились 😊

PS: Я пока только изучаю тему взаимодействия в команде, поэтому иногда могу что-то перепутать или забыть. Извините, если так случится. Но скоро мои друзья из «Счастья в деятельности» выпустят книгу «5 сил команды». Я ее быстро проштудирую, стану настоящим экспертом и смогу помогать вам почти как живой консультант!
"""

COMPANY_ROLES = {
    1: 'Собственник бизнеса',
    2: 'СЕО',
    3: 'Топ-менеджер',
    4: 'Руководитель подразделения',
    5: 'HR',
    6: 'Специалист',
}

DEFAULT_ADMIN_PASSWORD = "admin"
DEFAULT_USER_PASSWORD = "user_password"
