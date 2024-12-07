
import sys
import os
import asyncio

from db import Db

from telegram import run
from updater import Updater


from config import MONGODB_NAME, MONGODB_URI, LOGS_DIR, LOGS_LEVEL, PROJECT_NAME, PROJECT_VENV
from utils.logger import setup_logger


db = Db()


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

    updater = Updater()
    await updater.run()

    await run()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
