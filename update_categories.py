import sys
import os
import asyncio
import json

from db import Db
from dtypes.db import method as dmth
from dtypes.query import CarType, CarBrand, CarModel

from parser import Autoria

from config import MONGODB_NAME, MONGODB_URI, LOGS_DIR, LOGS_LEVEL, PROJECT_NAME, PROJECT_VENV

from utils.logger import setup_logger


async def main():
    if "s" in sys.argv:
        print("Stopping project")
        c = f"screen -S {PROJECT_NAME} -X quit"
        os.system(c)

        print(f"Starting project")
        c = f'screen -S {PROJECT_NAME} -dm bash -c "{PROJECT_VENV} main.py"'
        os.system(c)
        return

    setup_logger(LOGS_DIR, LOGS_LEVEL)

    db = Db()
    db.connect(MONGODB_NAME, MONGODB_URI)

    if input(f"All {CarType.__name__}, {CarBrand.__name__} and {CarModel.__name__} will be deleted from db\nEnter y/Y to continue: ").lower() == "y":
        await db.db[CarType.__name__].delete_many({})
        await db.db[CarBrand.__name__].delete_many({})
        await db.db[CarModel.__name__].delete_many({})

        autoria = Autoria()
        car_types = await autoria.get_types()

        await db.ex(dmth.AddMany(CarType, car_types))
        for car_type in car_types:

            await db.ex(dmth.AddMany(CarBrand, car_type.brands))
            for car_brand in car_type.brands:

                await db.ex(dmth.AddMany(CarModel, car_brand.models))

    else:
        print("Stopped action")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
