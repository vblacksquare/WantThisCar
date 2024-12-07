
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from db import Db
from dtypes.db import method as dmth
from dtypes.query import Query, QueryUpdate, CarType, CarModel, CarBrand
from dtypes.car import Car, gen_empty_car
from dtypes.destination import Destination

from parser import Autoria

from .destination import send_destination_msg

from telegram.factory import CallbackFactory

from config import UPDATER_DELAY
from utils import group_by, now


main_router = Router()
db = Db()
autoria = Autoria()


@main_router.callback_query(CallbackFactory.filter(F.action == "main"))
async def main_menu(callback: CallbackQuery = None, state: FSMContext = None, user_message: Message = None):
    if state:
        await state.clear()

    action = user_message.answer if user_message else callback.message.edit_text

    user_id = callback.from_user.id if callback else user_message.from_user.id
    destination: Destination = await db.ex(dmth.GetOne(Destination, id=user_id))
    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))

    if not destination:
        return await send_destination_msg(callback=callback, user_message=user_message, state=state)

    await update_query_cars(query)

    keyboard = InlineKeyboardBuilder()

    update_car_bts = [
        InlineKeyboardButton(
            text=_(f"update_car_type_bt"),
            callback_data=CallbackFactory(action="update_car_type").pack()
        ),
        InlineKeyboardButton(
            text=_(f"update_car_brand_bt"),
            callback_data=CallbackFactory(action="update_car_brand").pack()
        ),
        InlineKeyboardButton(
            text=_(f"update_car_model_bt"),
            callback_data=CallbackFactory(action="update_car_model").pack()
        )
    ]

    if not query.car_type:
        update_car_bts = update_car_bts[:1]

    elif not query.brand:
        update_car_bts = update_car_bts[:2]

    elif not query.model:
        pass

    else:
        keyboard.row(
            InlineKeyboardButton(
                text=_(f"update_is_running_{query.is_running}_bt"),
                callback_data=CallbackFactory(action="update_is_running").pack()
            )
        )

    for bt in update_car_bts:
        keyboard.row(bt)

    keyboard.row(
        InlineKeyboardButton(
            text=_(f"update_is_usa_{query.is_usa}_bt"),
            callback_data=CallbackFactory(action="update_is_usa").pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=_(f"update_is_accident_{query.is_accident}_bt"),
            callback_data=CallbackFactory(action="update_is_accident").pack()
        )
    )

    car_type = _(f"car_type_{query.car_type.id}") if query.car_type else _("option_empty")
    car_brand = query.brand.key if query.brand else _("option_empty")
    car_model = query.model.key if query.model else _("option_empty")

    await action(
        text=_("main_msg").format(
            type=car_type,
            brand=car_brand,
            model=car_model,
            is_usa=_(str(query.is_usa)),
            is_accident=_(str(query.is_accident)),
            is_running=_(f"is_running_{query.is_running}")
        ),
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


async def update_query_cars(query: Query):
    if not query.key:
        return

    query_update: QueryUpdate = await db.ex(dmth.GetOne(QueryUpdate, id=query.key))
    if not query_update:
        query_update = QueryUpdate(id=query.key, time=0)
        await db.ex(dmth.AddOne(QueryUpdate, query_update))

    time_now = now()
    if time_now - query_update.time > UPDATER_DELAY * 1.5:
        query_update.time = time_now
        await db.ex(dmth.UpdateOne(QueryUpdate, query_update, to_update=["time"]))

        car_ids = await autoria.search_by_query(query)
        for car_id in car_ids:
            car = gen_empty_car(id=car_id)
            await db.ex(dmth.AddOne(Car, car))


@main_router.callback_query(CallbackFactory.filter(F.action == "update_is_running"))
async def update_is_running(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))
    query.is_running = not query.is_running

    await db.ex(dmth.UpdateOne(Query, query, to_update=["is_running", "key"]))

    await main_menu(callback=callback, state=state)


@main_router.callback_query(CallbackFactory.filter(F.action == "update_is_usa"))
async def update_is_usa(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))
    query.is_usa = not query.is_usa

    await db.ex(dmth.UpdateOne(Query, query, to_update=["is_usa", "key"]))

    await main_menu(callback=callback, state=state)


@main_router.callback_query(CallbackFactory.filter(F.action == "update_is_accident"))
async def update_is_accident(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))
    query.is_accident = not query.is_accident

    await db.ex(dmth.UpdateOne(Query, query, to_update=["is_accident", "key"]))

    await main_menu(callback=callback, state=state)


@main_router.callback_query(CallbackFactory.filter(F.action == "update_car_type"))
async def update_car_type(callback: CallbackQuery, state: FSMContext):
    car_types: list[CarType] = await db.ex(dmth.GetMany(CarType))

    keyboard = InlineKeyboardBuilder()

    groups = group_by(car_types, k=2)
    for group in groups:
        keyboard.row(
            *[
                InlineKeyboardButton(
                    text=_(f"car_type_{car_type.id}"),
                    callback_data=CallbackFactory(action="updated_car_type", value=car_type.id).pack()
                )
                for car_type in group
            ]
        )

    keyboard.row(
        InlineKeyboardButton(
            text=_("back_bt"),
            callback_data=CallbackFactory(action="main").pack()
        )
    )

    await callback.message.edit_text(
        text=_("update_car_type_msg"),
        reply_markup=keyboard.as_markup()
    )


@main_router.callback_query(CallbackFactory.filter(F.action == "updated_car_type"))
async def updated_car_type(callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    car_type_id = callback_data.value
    car_type = await db.ex(dmth.GetOne(CarType, id=car_type_id))

    user_id = callback.from_user.id
    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))
    query.car_type = car_type
    query.brand = None
    query.model = None
    query.is_running = False

    await db.ex(dmth.UpdateOne(Query, query, to_update=["car_type", "brand", "model", "is_running", "key"]))

    await main_menu(callback=callback, state=state)


@main_router.callback_query(CallbackFactory.filter(F.action == "update_car_brand"))
async def update_car_brand(callback: CallbackQuery):
    user_id = callback.from_user.id
    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))

    car_type: CarType = await db.ex(dmth.GetOne(CarType, id=query.car_type.id))

    keyboard = InlineKeyboardBuilder()

    groups = group_by(car_type.brands, k=2)
    for group in groups:
        keyboard.row(
            *[
                InlineKeyboardButton(
                    text=car_brand.key,
                    callback_data=CallbackFactory(action="updated_car_brand", value=car_brand.id).pack()
                )
                for car_brand in group
            ]
        )

    keyboard.row(
        InlineKeyboardButton(
            text=_("back_bt"),
            callback_data=CallbackFactory(action="main").pack()
        )
    )

    await callback.message.edit_text(
        text=_("update_car_brand_msg"),
        reply_markup=keyboard.as_markup()
    )


@main_router.callback_query(CallbackFactory.filter(F.action == "updated_car_brand"))
async def updated_car_brand(callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    car_brand_id = callback_data.value
    car_brand = await db.ex(dmth.GetOne(CarBrand, id=car_brand_id))

    user_id = callback.from_user.id
    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))
    query.brand = car_brand
    query.model = None
    query.is_running = False

    await db.ex(dmth.UpdateOne(Query, query, to_update=["brand", "model", "is_running", "key"]))

    await main_menu(callback=callback, state=state)


@main_router.callback_query(CallbackFactory.filter(F.action == "update_car_model"))
async def update_car_model(callback: CallbackQuery):
    user_id = callback.from_user.id
    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))

    car_brand: CarBrand = await db.ex(dmth.GetOne(CarBrand, id=query.brand.id))

    keyboard = InlineKeyboardBuilder()

    groups = group_by(car_brand.models, k=3)
    for group in groups:
        keyboard.row(
            *[
                InlineKeyboardButton(
                    text=car_model.key,
                    callback_data=CallbackFactory(action="updated_car_model", value=car_model.id).pack()
                )
                for car_model in group
            ]
        )

    keyboard.row(
        InlineKeyboardButton(
            text=_("back_bt"),
            callback_data=CallbackFactory(action="main").pack()
        )
    )

    await callback.message.edit_text(
        text=_("update_car_brand_msg"),
        reply_markup=keyboard.as_markup()
    )


@main_router.callback_query(CallbackFactory.filter(F.action == "updated_car_model"))
async def updated_car_model(callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    car_model_id = callback_data.value
    car_model = await db.ex(dmth.GetOne(CarModel, id=car_model_id))

    user_id = callback.from_user.id
    query: Query = await db.ex(dmth.GetOne(Query, id=user_id))
    query.model = car_model

    await db.ex(dmth.UpdateOne(Query, query, to_update=["model", "key"]))

    await main_menu(callback=callback, state=state)
