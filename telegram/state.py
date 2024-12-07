
from aiogram.fsm.state import State, StatesGroup


class MainState(StatesGroup):
    skip: State = State()
    temp_message_id: str = None
