
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LinkPreviewOptions
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from loguru import logger

from db import Db
from dtypes import Car
from dtypes.db import method as dmth
from dtypes.user_car import UserCar

from telegram import bot, i18n
from telegram.factory import CarFactory

from utils import beautify_num

from config import MERCURY_CAR_PHOTO_ROOT


car_router = Router()
db = Db()


async def send_car_changed_price_message(old_car: Car, new_car: Car, user_car: UserCar, language: str = "uk"):
    try:
        await bot.send_message(
            text=i18n.gettext("car_changed_price_msg", locale=language).format(
                old=beautify_num(old_car.price),
                new=beautify_num(new_car.price),
            ),
            chat_id=user_car.chat_id,
            reply_to_message_id=user_car.message_id,
            parse_mode="html"
        )

    except Exception as err:
        logger.exception(err)

    await send_car_channel_message(new_car, channel_id=user_car.chat_id, message_id=user_car.message_id)


async def send_car_bought_message(user_car: UserCar, language: str = "uk"):
    try:
        await bot.send_message(
            text=i18n.gettext("car_removed_msg", locale=language),
            chat_id=user_car.chat_id,
            reply_to_message_id=user_car.message_id,
            parse_mode="html"
        )

    except Exception as err:
        logger.exception(err)


async def send_car_channel_message(car: Car, channel_id: str, move: int = 0, is_auction: bool = False, language: str = "uk", message_id: int = None) -> str:
    try:
        if is_auction:
            photos = car.photos_auction

        else:
            photos = car.photos

        keyboard = InlineKeyboardBuilder()

        template = "car_msg"
        if car.bidfax_link:
            template = "car_bidfax_msg"

            keyboard.row(
                InlineKeyboardButton(
                    text=i18n.gettext("auction_catalog_bt", locale=language) if not is_auction else i18n.gettext("autoria_catalog_bt", locale=language),
                    callback_data=CarFactory(action="change_catalog", id=car.id).pack()
                )
            )

        left = move - 1 if move > 0 else len(photos) - 1
        right = move + 1 if move < len(photos) - 1 else 0

        keyboard.row(
            InlineKeyboardButton(
                text=i18n.gettext("prev_photo_bt", locale=language),
                callback_data=CarFactory(action="move_catalog", id=car.id, move=left).pack()
            ),
            InlineKeyboardButton(
                text=i18n.gettext("next_photo_bt", locale=language),
                callback_data=CarFactory(action="move_catalog", id=car.id, move=right).pack()
            )
        )

        if message_id:
            action = bot.edit_message_text
            additional = {"message_id": message_id}

        else:
            action = bot.send_message
            additional = {}

        message = await action(
            text=i18n.gettext(template, locale=language).format(
                title=car.title,
                price=beautify_num(car.price),
                location=car.location,
                mileage=car.mileage,
                autoria=car.link,
                bidfax=car.bidfax_link,
                photo=photos[move],
                photo_i=move + 1,
                photo_amount=len(photos),
                source=i18n.gettext("auction_source" if is_auction else "autoria_source", locale=language)
            ),
            parse_mode="html",
            link_preview_options=LinkPreviewOptions(
                url=photos[move],
                show_above_text=True
            ),
            reply_markup=keyboard.as_markup(),
            chat_id=channel_id,
            **additional
        )

        return message.message_id

    except Exception as err:
        logger.exception(err)

        return 0


async def send_car_message(car: Car, message: Message, move: int = 0, is_auction: bool = False, is_edit: bool = False):
    try:
        if is_auction:
            photos = car.photos_auction

        else:
            photos = car.photos

        keyboard = InlineKeyboardBuilder()

        template = "car_msg"
        if car.bidfax_link:
            template = "car_bidfax_msg"

            keyboard.row(
                InlineKeyboardButton(
                    text=_("auction_catalog_bt") if not is_auction else _("autoria_catalog_bt"),
                    callback_data=CarFactory(action="change_catalog", id=car.id).pack()
                )
            )

        left = move - 1 if move > 0 else len(photos) - 1
        right = move + 1 if move < len(photos) - 1 else 0

        keyboard.row(
            InlineKeyboardButton(
                text=_("prev_photo_bt"),
                callback_data=CarFactory(action="move_catalog", id=car.id, move=left).pack()
            ),
            InlineKeyboardButton(
                text=_("next_photo_bt"),
                callback_data=CarFactory(action="move_catalog", id=car.id, move=right).pack()
            )
        )

        action = message.edit_text if is_edit else message.answer
        await action(
            text=_(template).format(
                title=car.title,
                price=beautify_num(car.price),
                location=car.location,
                mileage=car.mileage,
                autoria=car.link,
                bidfax=car.bidfax_link,
                photo=photos[move],
                photo_i=move + 1,
                photo_amount=len(photos),
                source=_("auction_source" if is_auction else "autoria_source")
            ),
            parse_mode="html",
            link_preview_options=LinkPreviewOptions(
                url=photos[move],
                show_above_text=True
            ),
            reply_markup=keyboard.as_markup()
        )

    except Exception as err:
        logger.exception(err)


@car_router.callback_query(CarFactory.filter(F.action == "move_catalog"))
async def main_menu(callback: CallbackQuery, callback_data: CarFactory):
    car: Car = await db.ex(dmth.GetOne(Car, id=callback_data.id))
    move = callback_data.move

    is_auction = callback.message.link_preview_options.url.startswith(MERCURY_CAR_PHOTO_ROOT)
    await send_car_message(
        car=car,
        message=callback.message,
        move=move,
        is_auction=is_auction,
        is_edit=True
    )


@car_router.callback_query(CarFactory.filter(F.action == "change_catalog"))
async def main_menu(callback: CallbackQuery, callback_data: CarFactory):
    car: Car = await db.ex(dmth.GetOne(Car, id=callback_data.id))

    is_auction = callback.message.link_preview_options.url.startswith(MERCURY_CAR_PHOTO_ROOT)
    await send_car_message(
        car=car,
        message=callback.message,
        move=0,
        is_auction=not is_auction,
        is_edit=True
    )
