
from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from loguru import logger

from db import Db
from dtypes.db import method as dmth
from dtypes.destination import Destination
from telegram.factory import CallbackFactory


invite_router = Router()
db = Db()


@invite_router.my_chat_member()
async def invite(event: ChatMemberUpdated):
    try:
        user_id = event.from_user.id
        chat_id = event.chat.id

        destination = await db.ex(dmth.GetOne(Destination, id=user_id))

        try:
            status_value = event.new_chat_member.status.value

        except Exception as err:
            status_value = event.new_chat_member.status

        if status_value == "administrator" and not destination:
            destination = Destination(
                id=user_id,
                chat_id=chat_id
            )
            await db.ex(dmth.AddOne(Destination, destination))

            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                InlineKeyboardButton(
                    text=_("skip_bt"),
                    callback_data=CallbackFactory(action="main").pack()
                )
            )

            await event.bot.send_message(
                text=_("added_channel_msg").format(title=event.chat.title),
                chat_id=user_id,
                reply_markup=keyboard.as_markup(),
                parse_mode="html"
            )

    except Exception as err:
        logger.exception(err)
