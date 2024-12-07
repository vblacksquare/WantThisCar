
from dtypes.db import DatabaseItem


class UserCar(DatabaseItem):
    def __init__(
        self,
        id: str,
        car_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        query_key: str,
    ):

        self.id = id
        self.car_id = car_id
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.query_key = query_key

        self.fields = ["id", "car_id", "user_id", "chat_id", "message_id", "query_key"]
