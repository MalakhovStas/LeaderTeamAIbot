from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ParseMode
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted, \
    MessageToEditNotFound, MessageCantBeEdited
from ..utils.exception_control import exception_handler_wrapper
from ..loader import dp, bot, alm, logger, Base
from ..config import DEBUG


async def delete_message(chat_id, message_id) -> bool:
    """Удаляет сообщения"""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except (MessageToDeleteNotFound, MessageCantBeDeleted) as exc:
        if DEBUG:
            logger.warning(f'HANDLERS Error: {chat_id=} | {message_id=} | {exc=}')
        return False
    else:
        return True


async def edit_message(chat_id, message_id) -> bool:
    """Редактирует сообщения"""
    try:
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id)
    except (MessageToEditNotFound, MessageCantBeEdited) as exc:
        if DEBUG:
            logger.warning(f'HANDLERS Error: {chat_id=} | {message_id=} | {exc=}')
        return False
    else:
        return True


async def sending_message(user_id, reply_text, keyboard, disable_w_p_p) -> Message:
    """Отправляет сообщение пользователю"""
    if len(reply_text) > 4000:
        for num_part in range(0, len(reply_text), 4000):
            await bot.send_message(
                chat_id=user_id,
                text=reply_text[num_part:num_part+4000],
                disable_web_page_preview=disable_w_p_p
            )
        sent_message = await bot.send_message(
            chat_id=user_id,
            text='-'*60,
            reply_markup=keyboard,
            disable_web_page_preview=disable_w_p_p
        )

    else:
        sent_message = await bot.send_message(
            chat_id=user_id,
            text=reply_text,
            reply_markup=keyboard,
            disable_web_page_preview=disable_w_p_p
        )
    return sent_message


@dp.message_handler(state='*')
@exception_handler_wrapper
async def get_message_handler(message: Message, state: FSMContext) -> None:
    """ Обработчик входящих сообщений """
    reply_text, keyboard, next_state = await alm.get_reply(update=message, state=state)
    # print(reply_text, keyboard, next_state)
    disable_w_p_p = False if reply_text in [] else True

    if last_handler_sent_message_id := await Base.button_search_and_action_any_collections(
            user_id=message.from_user.id,
            action='get',
            button_name='last_handler_sent_message_id', updates_data=True
    ):
        if await state.get_state() in [
            'FSMMainMenuStates:create_response_manually',
            'FSMMainMenuStates:submit_for_revision_task_response_manually'
        ]:
            await edit_message(
                chat_id=message.from_user.id, message_id=last_handler_sent_message_id)
        else:
            await delete_message(
                chat_id=message.from_user.id, message_id=last_handler_sent_message_id)

    if reply_text.strip().endswith(':ai:some_question'):
        reply_text = reply_text.rstrip(':ai:some_question')
        bot.parse_mode = None

    sent_message = await sending_message(
        user_id=message.from_user.id,
        reply_text=reply_text,
        keyboard=keyboard,
        disable_w_p_p=disable_w_p_p
    )

    bot.parse_mode = ParseMode.HTML

    await state.update_data(last_handler_sent_message_id=sent_message.message_id,
                            last_handler_sent_from_message_message_id=sent_message.message_id)

    # Base.updates_data['last_handler_sent_message_id'] = sent_message.message_id
    await Base.button_search_and_action_any_collections(
        user_id=message.from_user.id,
        action='add',
        button_name='last_handler_sent_message_id',
        updates_data=True,
        instance_button=sent_message.message_id
    )
    # Base.updates_data['last_handler_sent_from_message_message_id'] = sent_message.message_id
    await Base.button_search_and_action_any_collections(
        user_id=message.from_user.id,
        action='add',
        button_name='last_handler_sent_from_message_message_id',
        updates_data=True,
        instance_button=sent_message.message_id
    )

    if next_state:
        await state.set_state(next_state) if next_state != 'reset_state' \
            else await state.reset_state()

        await Base.button_search_and_action_any_collections(
            user_id=message.from_user.id,
            action='add',
            button_name='state', updates_data=True,
            instance_button=next_state if next_state != 'reset_state' else None
        )


@dp.callback_query_handler(lambda callback: callback.data, state='*')
@exception_handler_wrapper
async def get_call_handler(call: CallbackQuery, state: FSMContext) -> None:
    """ Обработчик обратного вызова со всех клавиатур"""
    reply_text, keyboard, next_state = await alm.get_reply(update=call, state=state)
    disable_w_p_p = False if call.data == 'TopUpBalance' else True

    if call.data in ['CreateNewTaskForResponseManually',
                     'SubmitForRevisionTaskResponseManually', 'RegenerateAIResponse']:
        await edit_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    else:
        await delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    if reply_text.strip().endswith(':ai:some_question'):
        reply_text = reply_text.rstrip(':ai:some_question')
        bot.parse_mode = None

    sent_message = await sending_message(
        user_id=call.from_user.id,
        reply_text=reply_text,
        keyboard=keyboard,
        disable_w_p_p=disable_w_p_p
    )
    bot.parse_mode = ParseMode.HTML

    await state.update_data(
        last_handler_sent_message_id=sent_message.message_id,
        last_handler_sent_from_call_message_id=sent_message.message_id
    )

    # Base.updates_data['last_handler_sent_message_id'] = sent_message.message_id
    await Base.button_search_and_action_any_collections(
        user_id=call.from_user.id,
        action='add',
        button_name='last_handler_sent_message_id',
        updates_data=True,
        instance_button=sent_message.message_id
    )
    # Base.updates_data['last_handler_sent_from_call_message_id'] = sent_message.message_id
    await Base.button_search_and_action_any_collections(
        user_id=call.from_user.id,
        action='add',
        button_name='last_handler_sent_from_call_message_id',
        updates_data=True,
        instance_button=sent_message.message_id
    )

    if next_state:
        await state.set_state(next_state) if next_state != 'reset_state' \
            else await state.reset_state()

        await Base.button_search_and_action_any_collections(
            user_id=call.from_user.id,
            action='add',
            button_name='state',
            updates_data=True,
            instance_button=next_state if next_state != 'reset_state' else None
        )
