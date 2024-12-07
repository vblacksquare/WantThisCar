
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from telegram.state import MainState
from utils import create_join_link


destination_router = Router()


async def send_destination_msg(state: FSMContext, callback: CallbackQuery = None, user_message: Message = None):
    if user_message:
        bot = user_message.bot
        action = user_message.answer

    else:
        bot = callback.bot
        action = callback.message.edit_text

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=_("add_channel_bt"),
            url=await create_join_link(
                bot=bot,
                is_channel=True
            )
        )
    )

    await action(
        text=_("no_destination_msg"),
        parse_mode="html",
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(MainState.skip)
