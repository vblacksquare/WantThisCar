
from aiogram import Router

from .utils import utils_router
from .invite import invite_router


actions_router = Router()
actions_router.include_routers(
    utils_router,
    invite_router
)
