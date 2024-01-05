""" Параметры машины состояний пользователя и администратора """
from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMCompanyMenuStates(StatesGroup):
    """Состояния пользователя в меню компания"""
    register_company = State()
    change_role = State()
    change_about_company = State()
    change_about_team = State()


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
