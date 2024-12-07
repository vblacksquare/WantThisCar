
from dtypes.db import DatabaseItem

from . import CarModel


class CarBrand(DatabaseItem):
    def __init__(
        self,
        id: str,
        key: str,
        models: list[str]
    ):

        self.id = id
        self.key = key
        self.models = [model if isinstance(model, CarModel) else CarModel(**model) for model in models]

        self.fields = ["id", "key", "models"]
