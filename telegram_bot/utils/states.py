""" Параметры машины состояний пользователя и администратора """
from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMGreetingScriptStates(StatesGroup):
    """Состояния пользователя в сценарии первого знакомства с новым пользователем"""
    start_greeting = State()
    get_fullname = State()
    get_company = State()
    get_role_in_company = State()
    get_contacts = State()
    get_about_command = State()
    get_about_company = State()


class FSMMainMenuStates(StatesGroup):
    """Состояния пользователя в основном меню"""
    main_menu = State()
    question_openai = State()
    submit_for_revision_task_question_openai = State()


class FSMPersonalCabinetStates(StatesGroup):
    """Состояния пользователя в меню личного кабинета"""
    personal_cabinet = State()
    change_fio = State()
    change_phone_number = State()
    change_email = State()
    change_username = State()


class FSMCompanyMenuStates(StatesGroup):
    """Состояния пользователя в меню компания"""
    register_company = State()
    change_role = State()
    change_about_company = State()
    change_about_team = State()


class FSMSevenPetalsStates(StatesGroup):
    """Состояния пользователя в сценарии опроса 'Семь лепестков'
    из таблицы - Опросник 7 источников.xlsx"""
    # _changeling - вопрос перевёртыш

    start_survey = State()
    end_survey = State()

    optimism_mobilizing = State()
    optimism_support = State()
    optimism_changeling = State()

    stream_changeling = State()
    stream_possibilities = State()
    stream_efficiency = State()

    sense_decent_financial_return = State()
    sense_doing_my_own_thing = State()
    sense_changeling = State()

    love_changeling = State()
    love_good_relation = State()
    love_confession = State()

    play_activity_is_game = State()
    play_creative = State()
    play_changeling = State()

    study_new_experience = State()
    study_changeling = State()
    study_do_what_i_like = State()

    impact_to_plan = State()
    impact_changeling = State()
    impact_achieve_my_goals = State()

    general_questions_happy_man = State()
    general_questions_happy_in_work = State()

    open_questions_pleasure = State()
    open_questions_irritation = State()


class FSMUtilsStates(StatesGroup):
    """Состояния пользователя для дополнительных инструментов"""
    ...


class FSMAdminStates(StatesGroup):
    """Состояния администраторов"""
    password_mailing = State()
    mailing = State()
    mailing_admins = State()

    change_user_balance = State()
    change_user_requests_balance = State()
    block_user = State()
    unblock_user = State()
    unload_payment_data_user = State()
