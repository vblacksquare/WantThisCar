
from dtypes.db import DatabaseItem

from config import AUTORIA_CAR_LINK


class Car(DatabaseItem):
    def __init__(
        self,
        id: str,
        price: int,
        mileage: int,
        location: str,
        key: str,
        title: str,
        year: int,
        vin: str,
        bidfax_link: str,
        lot_number: str,
        auction_name: str,
        photos: list[str],
        photos_auction: list[str],
        query_key: str,
        is_appeared: bool = True
    ):

        self.id = id
        self.price = price
        self.mileage = mileage
        self.location = location
        self.key = key
        self.title = title
        self.year = year
        self.vin = vin
        self.bidfax_link = bidfax_link
        self.lot_number = lot_number
        self.auction_name = auction_name
        self.photos = photos
        self.photos_auction = photos_auction
        self.query_key = query_key
        self.is_appeared = is_appeared

        self.fields = [
            "id", "price", "mileage", "location", "key", "title", "year", "vin", "bidfax_link",
            "lot_number", "auction_name", "photos", "photos_auction", "query_key", "is_appeared"
        ]

    @property
    def link(self):
        return AUTORIA_CAR_LINK.format(
            id=self.id,
            key=self.key
        )


def gen_empty_car(id: str) -> Car:
    return Car(
        id=id,
        price=0,
        mileage=0,
        location="",
        key="",
        title="",
        year=0,
        vin="",
        bidfax_link="",
        lot_number="",
        auction_name="",
        photos=[],
        photos_auction=[],
        query_key=""
    )
