
from dtypes.db import DatabaseItem


class User(DatabaseItem):
    def __init__(
        self,
        id: str,
        first_name: str,
        second_name: str,
        username: str,
        language: str,
    ):

        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.username = username
        self.language = language

        self.fields = [
            "id", "first_name", "second_name", "username", "language"
        ]
