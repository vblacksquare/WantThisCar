
from aiogram.filters.callback_data import CallbackData
from typing import Optional


class CallbackFactory(CallbackData, prefix="fab", sep="~"):
    action: str
    value: Optional[str] = None
    value1: Optional[str] = None


class CarFactory(CallbackFactory, prefix="fab"):
    action: str
    id: str
    move: Optional[int] = None
