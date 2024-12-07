
from dtypes.db import DatabaseItem


class Destination(DatabaseItem):
    def __init__(
        self,
        id: str,
        chat_id: str
    ):

        self.id = id
        self.chat_id = chat_id

        self.fields = ["id", "chat_id"]
