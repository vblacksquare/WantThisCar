
from dtypes.db import DatabaseItem


class QueryUpdate(DatabaseItem):
    def __init__(
        self,
        id: str,
        time: int
    ):

        self.id = id
        self.time = time

        self.fields = ["id", "time"]
