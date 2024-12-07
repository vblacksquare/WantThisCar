
from dtypes.db import DatabaseItem

from . import CarType, CarBrand, CarModel


class Query(DatabaseItem):
    def __init__(
        self,
        id: str,
        car_type: dict | CarType = None,
        brand: dict | CarBrand = None,
        model: dict | CarModel = None,
        is_usa: bool = False,
        is_accident: bool = False,
        is_running: bool = False,
        key: str = None
    ):

        self.id = id
        self.car_type = car_type if isinstance(car_type, CarType) or not car_type else CarType(**car_type)
        self.brand = brand if isinstance(brand, CarBrand) or not brand else CarBrand(**brand)
        self.model = model if isinstance(model, CarModel) or not model else CarModel(**model)
        self.is_usa = is_usa
        self.is_accident = is_accident
        self.is_running = is_running

        self.fields = ["id", "car_type", "brand", "model", "is_usa", "is_accident", "is_running", "key"]

    @property
    def key(self):
        if not self.is_running:
            return

        return "-".join([
            self.car_type.id,
            self.brand.id,
            self.model.id,
            str(self.is_usa),
            str(self.is_accident)
        ])
