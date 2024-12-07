
from aiogram import BaseMiddleware, Dispatcher, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .state import MainState

from db import Db

from config import COMMANDS


class ClearFsmMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, dispatcher: Dispatcher):
        super().__init__()
        self.bot = bot
        self.dp = dispatcher
        self.db = Db()

    async def __call__(self, handler, event: Message, data: dict):
        state: FSMContext = data.get("state")
        state_key = await state.get_state()

        if event.text and event.text.lower() in COMMANDS and state_key:
            await state.clear()

            if state_key == f"{MainState.__name__}:skip":
                return

            return await self.dp._process_update(bot=self.bot, update=data['event_update'])

        return await handler(event, data)
