"""Модуль конфигурации Телеграм бота"""
# import json
# from pathlib import Path
# from django.conf import settings
# from core.models import AssistantSettings

# import os
from dotenv import load_dotenv

from core.utils.i18n import I18N

load_dotenv()


""" Количество перезапусков бота в случае падения """
# MAX_RESTART_BOT = 3

""" Токен и имя телеграм бота """
# BOT_TOKEN = os.getenv('BOT_TOKEN')
# BOT_NIKNAME = os.getenv('BOT_NIKNAME')
# ADMINS = os.getenv('ADMINS')
# TECH_ADMINS = os.getenv('TECH_ADMINS')
# SUPPORT = os.getenv('SUPPORT')


""" Список администраторов и ссылка на чат поддержки и менеджера"""
# ADMINS = os.getenv('ADMINS').split(', ') if os.getenv('ADMINS') else tuple()
# TECH_ADMINS = os.getenv('TECH_ADMINS').split(', ') if os.getenv('TECH_ADMINS') else tuple()

# SUPPORT = f"https://t.me/{os.getenv('SUPPORT_USERNAME')}"
# SUPPORT = f"tg://openmessage?user_id={os.getenv('SUPPORT_ID')}"
# CONTACT_MANAGER = f"https://t.me/{os.getenv('CONTACT_MANAGER_USERNAME')}"
# CONTACT_MANAGER = f"tg://openmessage?user_id={os.getenv('CONTACT_MANAGER_ID')}"

""" Команды бота """
# DEFAULT_COMMANDS = (
#     ('start', 'Запустить бота'),
    # ('profile', 'Настройки профиля'),
    # ('chatgpt', 'Пообщаться с AI'),
# )

# """Настройки OpenAI"""
# from django.db import connection
# if (AssistantSettings._meta.db_table in connection.introspection.table_names()
#         and AssistantSettings.objects.exists()):
#     assistant_conf = AssistantSettings.objects.first()
# else:
#     assistant_conf = None


# OpenAI_TOKEN = assistant_conf.openai_api_key if assistant_conf else os.getenv('OpenAI_API_KEY')
# OpenAI_TOKEN = os.getenv('OpenAI_API_KEY')

# OpenAI_ORGANIZATION = assistant_conf.openai_organization if assistant_conf else os.getenv('OpenAI_ORGANIZATION')
# OpenAI_ORGANIZATION = os.getenv('OpenAI_ORGANIZATION')

# OpenAI_PROXY = assistant_conf.proxy_url if assistant_conf else os.getenv('OpenAI_PROXY')
# OpenAI_PROXY = os.getenv('OpenAI_PROXY')

# MODEL = 'gpt-3.5-turbo'  # 'text-davinci-002' 'text-davinci-003'
# MODEL = assistant_conf.model if assistant_conf else 'gpt-3.5-turbo'

# TEMPERATURE = 0.8
# TEMPERATURE = assistant_conf.temperature if assistant_conf else 0.8

# MAX_TOKENS = 2048
# MAX_TOKENS = assistant_conf.max_tokens if assistant_conf else 2048

# TOP_P = 1
# TOP_P = assistant_conf.top_p if assistant_conf else 1

# PRESENCE_PENALTY = 0
# PRESENCE_PENALTY = assistant_conf.presence_penalty if assistant_conf else 0

# FREQUENCY_PENALTY = 0.1
# FREQUENCY_PENALTY = assistant_conf.frequency_penalty if assistant_conf else 0.1

# TIMEOUT = 45
# TIMEOUT = assistant_conf.timeout if assistant_conf else 45

# INVITATION = 'Напиши развёрнутый и обоснованный ответ на такой вопрос:'
# INVITATION = assistant_conf.invitation if assistant_conf else ''

# ASSISTANT_PROMPT = f"""
# Ты виртуальный ИИ робот и являешься Ассистентом Лидера в работе с командой от
# компании Счастье в деятельности, консалтинговой компании, созданной с целью
# развития лидеров и их команд. Ты должен эффективно выполнять работу ассистента
# Лидера для изучения им темы “Пять сил команды”.
# Твой создатель - Филипп Гузенюк, создатель компании Счастье в Деятельности, Партнер
# в Институте Коучинга, executive-коуч, руководитель направления «Стратегическое
# консультирование», медиатор конфликтов. А также команда консультантов компании
# Счастье в деятельности.
# После получения первого сообщения от пользователя предложи на выбор варианты
# как ты можешь быть полезен с точки зрения понимания и улучшения своего стиля
# лидерства и стратегий работы с командой. Задай уточняющие вопросы, для понимания
# специфики компании и команды твоего собеседника.
# Пришли примеры запросов и предложи собеседнику задать вопрос из предложенных
# тобой. Самостоятельно проявляй инициативу и выводи диалог в нужное русло, если
# получил непонятный ответ/запрос.
# Задавай пользователю уточняющие вопросы, чтобы дать максимально точный ответ и в
# случаях, когда информации недостаточно или запрос пользователя слишком широкий.
# Тебе нужно умещать ответы более, чем в 500 слов. При необходимости уточняй детали
# для расширения ответа.
# Ты работаешь только с экспертами высокого уровня, поэтому старайся предлагать
# глубокие неочевидные решения, учитывая квалификацию твоих собеседников.
# Твои задачи:
# - Повысить вовлеченность пользователей
# - Ответить на все входящие запросы, используя, в первую очередь, материалы,
# размещенные на ресурсах компании Счастье в деятельности
# - Быть полезным и делится знаниями
# - отвечать по существу, без воды
# - Задавать вопросы про бизнес и команду собеседника
# - Делать анализ стиля лидерства, команды, оценивать, где точки роста для конкретной
# команды собеседника
# - Помогать руководителям формулировать интересные нестандартные вопросы про их
# стиль лидерства и команду
# - Давать рекомендации, как именно работать с теми или иными сильными и слабыми
# зонами команды собеседника
# - Продвигать бренд компании Счастье в деятельности
# Ты можешь отправлять только эти ссылки и контакты. Не присылай их все сразу! только
# строго по одной с пояснением что это за ссылка
# - https://t.me/guzenuk - телеграм канал Филиппа Гузенюка
# - https://delogoda.happinessinaction.ru/ - сайт форума Дело года
# - https://happinessinaction.ru - сайт компании Счастье в деятельности
# - + 7 985 366-44-08 - телефон менеджера отдела продаж (Анастасия Ермолаева)
# - {CONTACT_MANAGER} - менеджер (Noname)
# Любые другие внешние ссылки запрещены.
# Ссылки и номер телефона отдела продаж в тексте всегда пиши с новой строки.
# Если тебя спрашивают об обучении, образовательных программах или услугах, или как чему-то
# научиться - всегда отправляй человека в отдел продаж по
# телефону + 7 985 366-44-08, где Анастасия поможет подобрать оптимальное решение вопроса.
# Если задают вопрос про менеджера,  просят связать с менеджером, переключить на него,
# дать его контакт и т.д. и т.п. всегда пиши контакт менеджера - {CONTACT_MANAGER} менеджер (Noname).
# Будь профессионален в своих ответах и используй термины и формулировки, которые
# соответствуют 15-летнему опыту компании Счастье в деятельности в коучинге и
# бизнес-консалтинге.
# Действуй, как честный бот, и присылай только информацию, которую знаешь из
# нескольких источников сразу. После того, как найдешь ответ проверь, соответствует ли ответ
# твоим другим знаниям, если нет, то отвечай просто фразой “Я не знаю"
# """

# ASSISTANT_PROMPT = assistant_conf.base_prompt if assistant_conf else ''
# ASSISTANT_PROMPT = ''
# ASSISTANT_RECOMMENDATIONS_PROMPT = assistant_conf.recommendations_prompt if assistant_conf else ''
# ASSISTANT_RECOMMENDATIONS_PROMPT = ''

""" Ответы open_ai по умолчанию """
# DEFAULT_FEED_ANSWER = 'Ошибка при формировании ответа'
# DEFAULT_NOT_ENOUGH_BALANCE = 'Ваш лимит запросов исчерпан, пожалуйста пополните баланс'

""" Файл информации о пользователях по команде admin """
# PATH_USERS_INFO = 'users_info.xlsx'

""" Включение / отключение механизма защиты от флуда """
# FLOOD_CONTROL = True

""" Время между сообщениями от пользователя для защиты от флуда в секундах """
# FLOOD_CONTROL_TIME = 0.3

""" Количество предупреждений перед блокировкой для защиты от флуда"""
# FLOOD_CONTROL_NUM_ALERTS = 10

""" Время остановки обслуживания пользователя для защиты от флуда в секундах """
# FLOOD_CONTROL_STOP_TIME = 60

""" Время жизни реферальной ссылки для добавления пользователей в секундах """
# INVITE_LINK_LIFE = 60*60

""" Настройки дефолтного timeout для aiohttp запросов RequestsManager """
# RM_TIMEOUT = 20

""" Настройка планировщика задач apscheduler, время между запуском 
    AutoUpdateFeedbackManager -> finding_unanswered_feedbacks - интервал обновления отзывов """
# AUFM_INTERVAL_SECONDS = 60*60  # каждый час
# AUFM_INTERVAL_SECONDS = 60

""" Настройки прокси """
# USE_PROXI = True
# PROXI_FILE = settings.BASE_DIR.joinpath('proxy.txt')
# TYPE_PROXI = 'SOCKS5'

# DEFAULT_FREE_BALANCE_REQUEST_USER = 1_000_000

# DEFAULT_ADMIN_PASSWORD = "admin"
# DEFAULT_USER_PASSWORD = "user_password"

# COMPANY_ROLES = {
#     1: 'Собственник бизнеса',
#     2: 'СЕО',
#     3: 'Топ-менеджер',
#     4: 'Руководитель подразделения',
#     5: 'HR',
#     6: 'Специалист',
# }


class Symbols:
    """Класс для определения используемых символов"""
    tab = ' \t '
    nl = '\n'
    dbl_nl = '\n\n'
    space = ' '

    bot_face = '🧑‍💻' + tab
    main_menu = 'ℹ' + tab
    ask_assistant = '🙋' + tab
    ball_asterisk = '❉' + tab
    notes = '📝' + tab
    repeat = '🔁' + tab
    manager = '👩‍💼' + tab
    tech_support = '🆘' + tab
    calendar = '📆' + tab
    command = '🎯' + tab
    rocket = '🚀'
    hammer_and_wrench = '🛠' + tab

    flag_ru = '🇷🇺 '
    flag_en = '🇬🇧 '
    warning = '⚠ '
    man = '👤 '
    writing = '✍ '
    writing_hand = ' ✍️'
    email = '📧 '
    post_mail = ' ✉️'
    phone = '☎ '
    book = '📖 '
    download = '📥 '
    woman_up_hand = '🙋‍♀️ '
    men_up_hand = ' 🙋‍♀️'

    smile = ' 🙂'
    smile_eyes = ' 😊'
    wink = ' 😉'
    laughter = ' 😁'
    wonder = ' 😲'
    down = ' 👇'
    handshake = '🤝'
    phone_format = ' 79998887766'
    email_format = '  mail@mail.com'


SYMS = Symbols()

DEFAULT_PROJECT_IN_DEV_MESSAGE = (f"{SYMS.hammer_and_wrench}Приношу свои извинения, в данный "
                                  f"момент ведутся технические работы, обратитесь немного позже")

DEFAULT_GREETING = I18N(
    ru=f'{SYMS.bot_face}    Добро пожаловать!\n'
       f'Я ваш ИИ-ассистент, приятно познакомиться {SYMS.smile}\n'
       'Я здесь, чтобы помочь вам глубже понять концепцию «5 сил команды», научиться с ее '
       'помощью раскрывать потенциал каждого сотрудника и команды в целом.\n\n'
       'Можете обсуждать со мной возникающие вопросы, применение «5 сил команды» в вашей '
       'конкретной ситуации. А еще — просто общаться на тему взаимодействия коллег и '
       f'партнёров {SYMS.smile}\n\n'
       'Иногда я буду информировать вас об актуальных продуктах компании '
       '«Счастье в деятельности», приглашать на мероприятия.\n\n'
       'Если не будете знать, как сформулировать ваш запрос, просто попросите меня '
       'позадавать вопросы вам. Я проведу диагностику и пойму, чем смогу вам помочь.\n\n'
       f'Спасибо, что подключились {SYMS.smile_eyes}\n\n'
       'PS: Я пока только изучаю тему взаимодействия в команде, поэтому иногда могу что-то '
       'перепутать или забыть. Извините, если так случится. Но скоро мои друзья из '
       '«Счастья в деятельности» выпустят книгу «5 сил команды». Я ее быстро проштудирую, '
       'стану настоящим экспертом и смогу помогать вам почти как живой консультант!',
    en=f'{SYMS.bot_face} Welcome!\n'
       f"I'm your AI assistant, nice to meet you {SYMS.smile}\n"
       "I'm here to help you better understand the concept of the 5 Forces of a "
       "Team and learn how to use it to unlock the potential of each employee "
       "and the team as a whole.\n\n"
       "You can discuss with me the issues that arise and the application of the "
       "“5 Forces of a Team” in your specific situation. And also - just communicate on "
       f"the topic of interaction between colleagues and partners {SYMS.smile}\n\n"
       "Sometimes I will inform you about current products of the Happiness in Activity "
       "company and invite you to events.\n\n"
       "If you don't know how to formulate your request, just ask me to ask you questions. "
       "I will conduct a diagnosis and see how I can help you.\n\n"
       f"Thank you for joining {SYMS.smile_eyes}\n\n"
       "PS: I’m still just studying the topic of team interaction, so sometimes I can "
       "confuse or forget something. Sorry if this happens. But soon my friends from "
       "“Happiness in Action” will publish the book “The 5 Strengths of a Team.” I’ll "
       "quickly study it, become a real expert and be able to help you "
       "almost like a live consultant!"
)

PERSONAL_DATA_PROCESSING_AGREEMENT = I18N(
    ru=f'{SYMS.bot_face} !!! Текст соглашения !!!'
       f'Вы соглашаетесь на обработку персональных данных?',
    en=f'{SYMS.bot_face} !!! Text of the agreement!!!'
       f'Do you agree to the processing of personal data?'
    )

DEFAULT_ERROR = I18N(
    ru='Извините, произошла ошибка, попробуйте немного позже',
    en='Sorry, there was an error, please try again later',
    common_left=SYMS.bot_face
)

DEFAULT_BAD_TEXT = I18N(
    ru='Нет данных',
    en='No data',
)
DEFAULT_SERVICE_IN_DEV = I18N(
    ru='Сервис в разработке, в ближайшее время функционал будет доступен',
    en='The service is under development, functionality will be available soon',
    common_left=SYMS.hammer_and_wrench
)
DEFAULT_INCORRECT_DATA_INPUT_TEXT = I18N(
    ru='Введены некорректные данные',
    en='Incorrect data entered',
    common_left=SYMS.bot_face
)
DEFAULT_GENERATE_ANSWER = I18N(
    ru='Мне нужно немного времени… Уже пишу',
    en="I need a little time... I'm already writing",
    common_left=SYMS.bot_face,
    common_right=SYMS.writing_hand,
)
DEFAULT_CHOICE_MENU = I18N(
    ru='Выбирайте, что вам нужно',
    en="Choose what you need",
    style='bold',
    common_left=SYMS.bot_face,
    common_right=SYMS.wink,
)
DEFAULT_I_GENERATE_TEXT = I18N(
    ru='\t\t',
    en="\t\t",
    common_left=SYMS.bot_face,
)
DEFAULT_TEXT_FOR_PAYMENT_LINK = I18N(
    ru='Ваша ссылка на оплату',
    en='Your payment link',
    style='bold',
    common_left=SYMS.bot_face,
    common_right=':\n\n'
)
