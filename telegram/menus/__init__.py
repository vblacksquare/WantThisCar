
from aiogram import Router

from .auth import auth_router
from .actions import actions_router
from .language import language_router
from .main import main_router
from .car import car_router
from .destination import destination_router


menus_router = Router()
menus_router.include_routers(
    auth_router,
    actions_router,
    language_router,
    main_router,
    car_router,
    destination_router
)
