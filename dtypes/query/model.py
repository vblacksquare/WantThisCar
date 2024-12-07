
from dtypes.db import DatabaseItem


class CarModel(DatabaseItem):
    def __init__(
        self,
        id: str,
        key: str
    ):

        self.id = id
        self.key = key

        self.fields = ["id", "key"]
