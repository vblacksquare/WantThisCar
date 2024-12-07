
import asyncio
import copy
import uuid

from loguru import logger

from db import Db

from parser.autoria import Autoria
from dtypes.query import Query, QueryUpdate
from dtypes.db import method as dmth
from dtypes.car import Car
from dtypes.user_car import UserCar
from dtypes.destination import Destination

from telegram.menus.car import send_car_channel_message, send_car_bought_message, send_car_changed_price_message

from config import UPDATER_DELAY
from utils.singleton import SingletonMeta
from utils import now


autoria = Autoria()


class Updater(metaclass=SingletonMeta):
    def __init__(self):
        self.db = Db()
        self.log = logger.bind(classname=self.__class__.__name__)

        self.tasks = [self.search_new_cars, self.update_cars]

        self.delay = UPDATER_DELAY

    async def process_new_car(self, car_id: str, query: Query, user_ids: list[str]):
        car = await autoria.get_car(
            id=car_id,
            brand=query.brand.key.lower(),
            model=query.model.key.lower(),
            query_key=query.key
        )

        if not car:
            return

        await self.db.ex(dmth.AddOne(Car, car))

        destinations: list[Destination] = await self.db.ex(dmth.GetMany(Destination, id={"$in": user_ids}))
        for destination in destinations:
            message_id = await send_car_channel_message(
                car=car,
                channel_id=destination.chat_id,
            )

            user_car = UserCar(
                id=uuid.uuid4().hex,
                car_id=car.id,
                user_id=destination.id,
                message_id=message_id,
                chat_id=destination.chat_id,
                query_key=query.key
            )
            await self.db.ex(dmth.AddOne(UserCar, user_car))

    async def search_new_cars(self):
        queries: list[Query] = await self.db.ex(dmth.GetMany(Query, is_running=True))
        duplicates = {}

        for query in queries:
            if query.key in duplicates:
                duplicates[query.key]["users"].append(query.id)

            else:
                duplicates.update({
                    query.key: {
                        "query": query,
                        "users": [query.id]
                    }
                })

        tasks = []
        for key in duplicates:
            query_update: QueryUpdate = await self.db.ex(dmth.GetOne(QueryUpdate, id=key))
            if not query_update:
                query_update = QueryUpdate(id=key, time=0)
                await self.db.ex(dmth.AddOne(QueryUpdate, query_update))

            query_update.time = now()
            await self.db.ex(dmth.UpdateOne(QueryUpdate, query_update, to_update=["time"]))

            query = duplicates[key]["query"]
            user_ids = duplicates[key]["users"]

            car_ids = await autoria.search_by_query(query)
            temp_car_ids = [car.id for car in await self.db.ex(dmth.GetMany(Car, id={"$in": car_ids}))]

            self.log.debug(f"Temp car_ids -> {temp_car_ids}")

            for car_id in car_ids:
                if car_id in temp_car_ids:
                    continue

                tasks.append(self.process_new_car(car_id=car_id, query=query, user_ids=user_ids))

        for task in tasks:
            await task

    async def process_update_car(self, car: Car, query: Query, user_ids: list[str]):
        new_car = await autoria.get_car(id=car.id, brand=query.brand.key.lower(), model=query.model.key.lower(), query_key=query.key)

        if not new_car:
            car.is_appeared = False
            await self.db.ex(dmth.UpdateOne(Car, car, to_update=["is_appeared"]))

            user_cars: list[UserCar] = await self.db.ex(dmth.GetMany(UserCar, car_id=car.id))
            for user_car in user_cars:
                await send_car_bought_message(user_car)

        elif new_car.price != car.price:
            old_car = copy.deepcopy(car)

            car.price = new_car.price
            await self.db.ex(dmth.UpdateOne(Car, car, to_update=["price"]))

            user_cars: list[UserCar] = await self.db.ex(dmth.GetMany(UserCar, car_id=car.id))
            for user_car in user_cars:
                await send_car_changed_price_message(old_car, new_car, user_car)

    async def update_cars(self):
        queries: list[Query] = await self.db.ex(dmth.GetMany(Query, is_running=True))
        duplicates = {}

        for query in queries:
            if query.key in duplicates:
                duplicates[query.key]["users"].append(query.id)

            else:
                duplicates.update({
                    query.key: {
                        "query": query,
                        "users": [query.id]
                    }
                })

        tasks = []
        for key in duplicates:
            query = duplicates[key]["query"]
            user_ids = duplicates[key]["users"]
            cars: list[Car] = await self.db.ex(dmth.GetMany(Car, query_key=key, is_appeared=True))

            for car in cars:
                tasks.append(self.process_update_car(car=car, query=query, user_ids=user_ids))

        for task in tasks:
            await task

    async def __run(self):
        while True:
            await asyncio.sleep(self.delay)
            await asyncio.gather(*[task() for task in self.tasks])


    async def run(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.__run())
