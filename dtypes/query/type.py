
from dtypes.db import DatabaseItem

from . import CarBrand


class CarType(DatabaseItem):
    def __init__(
        self,
        id: str,
        key: str,
        brands: list[dict | CarBrand],
    ):

        self.id = id
        self.key = key
        self.brands = [brand if isinstance(brand, CarBrand) else CarBrand(**brand) for brand in brands]

        self.fields = ["id", "key", "brands"]
