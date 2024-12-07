
import aiohttp

from bs4 import BeautifulSoup
import json

from loguru import logger

from dtypes.query import Query, CarType, CarBrand, CarModel
from dtypes.car import Car

from utils.singleton import SingletonMeta

from .serp import find_lot_number

from config import AUTORIA_ROOT, AUTORIA_BRANDS_ALL_LINK, AUTORIA_BRANDS_TOP_LINK, AUTORIA_MODELS_TOP_LINK, AUTORIA_CAR_LINK, BIDFAX_ROOT, MERCURY_CAR_PHOTO_LINK


class Autoria(metaclass=SingletonMeta):
    def __init__(self):
        self.log = logger.bind(classname=self.__class__.__name__)

    async def search_by_query(self, query: Query) -> list[str]:
        data = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url="https://auto.ria.com/api/search/auto",
                    params={
                        "indexName": "auto,order_auto,newauto_search",
                        "category_id": int(query.car_type.id),
                        "marka_id[0]": int(query.brand.id),
                        "model_id[0]": int(query.model.id),
                        "excludeUSA": query.is_usa + 1,
                        "damage": query.is_accident + 1,
                        "order_by": 7,
                        "abroad": 2,
                        "custom": 3,
                        "page": 0,
                        "countpage": 10,
                        "with_feedback_form": 1,
                        "withOrderAutoInformer": 1,
                        "with_last_id": 1
                    }
                ) as resp:
                    self.log.debug(f"Got resposne -> {resp}")

                    data = await resp.json()

        except Exception as err:
            self.log.exception(err)

        cars_ids = []
        try:
            cars_ids = data["result"]["search_result"]["ids"]

        except Exception as err:
            self.log.exception(err)

        # generate auto.ria ids -> audi_a8_2103910230
        return [
            "_".join([query.brand.key.lower(), query.model.key.lower(), car_id])
            for car_id in cars_ids
        ]

    async def get_car(self, id: str, brand: str, model: str, query_key: str) -> Car | None:
        data = None
        link = AUTORIA_CAR_LINK.format(id=id)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=link
                ) as resp:

                    self.log.debug(f"Got resposne -> {resp}")
                    data = await resp.text()

        except Exception as err:
            self.log.exception(err)

        car = None
        try:
            soup = BeautifulSoup(data, "html.parser")

            # find embedded json to speed up parsing
            json_data = json.loads(soup.select_one("#ldJson2").get_text())

            price = int(json_data["offers"]["price"])
            mileage = int(json_data["mileageFromOdometer"]["value"])
            year = int(json_data["productionDate"])
            title = json_data["name"]

            # sometimes vin going to be with the other selector
            vin = soup.select_one("span.label-vin")
            if not vin:
                vin = soup.select_one("span.vin-code")
            if vin:
                vin = vin.get_text(strip=True)

            location = soup.select_one("div.item[data-query*='type=city&cityId=']").get_text(strip=True)
            photos = [img.get("src") for img in soup.select("#photosBlock div.gallery-order div[class*='photo'] img")]

            try:
                bidfax_redirect = soup.select_one("script[data-technical-report]").get("data-bidfax-pathname")
                bidfax_link = '/'.join((
                    BIDFAX_ROOT,
                    bidfax_redirect.split("/", maxsplit=2)[-1]
                )) if bidfax_redirect else None

            except Exception as err:
                self.log.warning(f"No bidfax link for car {link}")

                bidfax_link = None

            # next steps are to collect enought data to generate auction photos
            # auction_name and lot_number is required for url (you can find template in config.py -> MERCURY_CAR_PHOTO_LINK)

            # auction_name located in description or tooltips
            auction_name = None
            if bidfax_link:
                try:
                    text = ''.join((
                        soup.select_one("div.m-padding").get_text(),
                        '\n'.join((
                            str(el.get("data-tooltip"))
                            for el in soup.select("span[data-tooltip]")
                        ))
                    )).lower().replace("і", "i").replace("а", "a")

                    if "iaai" in text:
                        auction_name = "iaai"

                    elif "copart" in text:
                        auction_name = "copart"

                    else:
                        raise ValueError

                except Exception as err:
                    self.log.warning("Can't get auction name")

            # lot_number is not located somewhere on auto.ria so it have to be gotten somewhere else
            # the only way I found without using selenium is to get it from bidfax.info car preview in google search
            # this is not perfect but is pretty good in comparison to others

            lot_number = None
            if auction_name:
                lot_number = await find_lot_number(bidfax_link)

            photos_auction = []
            if lot_number and vin:
                title_parts = title.split(" ")

                if title_parts[-1].isdigit():
                    car_name = " ".join(title_parts[:-1])

                elif title_parts[0].isdigit():
                    car_name = " ".join(title_parts[1:])

                else:
                    car_name = title

                for i in range(1, 11):
                    photos_auction.append(
                        MERCURY_CAR_PHOTO_LINK.format(
                            id=0 if auction_name == "iaai" else 1,
                            lot=lot_number,
                            year=year,
                            car_name=car_name.replace(' ', '-'),
                            vin=vin,
                            i=i
                        )
                    )

            car = Car(
                id=id,
                price=price,
                mileage=round(mileage/1000),
                location=location,
                title=title,
                year=year,
                key="_".join((brand, model)),
                vin=vin,
                bidfax_link=bidfax_link,
                lot_number=lot_number,
                auction_name=auction_name,
                photos=photos,
                photos_auction=photos_auction,
                query_key=query_key
            )

        except Exception as err:
            self.log.exception(err)

        return car

    async def __get_models(self, car_type_id: str, car_brand_id: str) -> list[CarModel]:
        """Getting top models according to car type and brand"""

        data = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=AUTORIA_MODELS_TOP_LINK.format(
                        type_id=car_type_id,
                        brand_id=car_brand_id
                    ),
                    params={
                        "langId": 4,
                        "withNew": 1
                    }
                ) as resp:
                    self.log.debug(f"Got resposne -> {resp}")
                    data = await resp.json()

        except Exception as err:
            self.log.exception(err)

        if not data:
            return []

        car_models = []

        try:
            raw_car_models = data
            for raw_car_model in raw_car_models:
                car_model_id = raw_car_model["value"]
                key = raw_car_model["name"]

                car_model = CarModel(
                    id=str(car_model_id),
                    key=key
                )

                car_models.append(car_model)

        except Exception as err:
            self.log.exception(err)

        return car_models

    async def __get_brands(self, car_type_id: str) -> list[CarBrand]:
        """
        2 requests is needed because of locales.
        First is for top brands that it has to return (returns only ids).
        Second is for all brands with locales.
        """

        data = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=AUTORIA_BRANDS_TOP_LINK,
                    params={
                        "id": car_type_id
                    }
                ) as resp:
                    self.log.debug(f"Got resposne -> {resp}")
                    data = await resp.json()

        except Exception as err:
            self.log.exception(err)

        top_brands = []
        if data:
            try:
                top_brands = data["marka"]

            except Exception as err:
                self.log.exception(err)

        data = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=AUTORIA_BRANDS_ALL_LINK.format(id=car_type_id),
                    params={
                        "langId": 4
                    }
                ) as resp:
                    self.log.debug(f"Got resposne -> {resp}")
                    data = await resp.json()

        except Exception as err:
            self.log.exception(err)

        if not data:
            return []

        car_brands = []

        try:
            raw_car_brands = data
            for raw_car_brand in raw_car_brands:
                car_brand_id = raw_car_brand["value"]
                if car_brand_id not in top_brands:
                    continue

                key = raw_car_brand["name"]

                car_brand = CarBrand(
                    id=str(car_brand_id),
                    key=key,
                    models=await self.__get_models(car_type_id, car_brand_id)
                )

                car_brands.append(car_brand)

        except Exception as err:
            self.log.exception(err)

        return car_brands

    async def get_types(self) -> list[CarType]:
        """
        Just a recurcive function to get all car types, brands and models.
        It is built like this because model depends on brand and brand on type
        """

        data = None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=AUTORIA_ROOT
                ) as resp:
                    self.log.debug(f"Got resposne -> {resp}")
                    data = await resp.text()

        except Exception as err:
            self.log.exception(err)

        if not data:
            return []

        car_types = []
        try:
            soup = BeautifulSoup(data, "html.parser")

            raw_car_types = soup.select("#categories option")

            for raw_car_type in raw_car_types:
                car_type_id = raw_car_type["value"]

                if int(car_type_id) == 0:
                    continue

                car_type = CarType(
                    id=str(car_type_id),
                    key=None,
                    brands=await self.__get_brands(car_type_id)
                )

                car_types.append(car_type)

        except Exception as err:
            self.log.exception(err)

        return car_types
