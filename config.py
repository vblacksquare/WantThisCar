
import os


PROJECT_NAME = "WantThisCar"
PROJECT_VENV = "venv/bin/python"


# telegram
BOT_TOKEN = ""  # https://t.me/botfather
COMMANDS = ["/start"]
LANGUAGES = ["uk"]
DEFAULT_LANGUAGE = LANGUAGES[0]


# db
MONGODB_URI = ""    # https://www.mongodb.com/community/forums/t/how-to-host-your-own-mongodb-server-without-using-hosting-providers/14435
MONGODB_NAME = "WantThisCar"


# auto.ria.com
AUTORIA_ROOT = "https://auto.ria.com/"
AUTORIA_BRANDS_TOP_LINK = "https://auto.ria.com/demo/bu/mainPage/categories/popularBrands"
AUTORIA_BRANDS_ALL_LINK = "https://auto.ria.com/demo/api/categories/{id}/brands/_active/_with_count/_with_country"
AUTORIA_MODELS_TOP_LINK = "https://auto.ria.com/api/categories/{type_id}/marks/{brand_id}/models/_active/_with_count"
AUTORIA_CAR_LINK = "https://auto.ria.com/uk/auto_{id}.html"

# bidfax.info
BIDFAX_ROOT = "https://bidfax.info"

# mercury.bid.cars
MERCURY_CAR_PHOTO_LINK = "https://mercury.bid.cars/{id}-{lot}/{year}-{car_name}-{vin}-{i}.jpg"
MERCURY_CAR_PHOTO_ROOT = "https://mercury.bid.cars"

# serpapi.com
SERPAPI_ROOT = "https://google.serper.dev/search"
SERPAPI_TOKEN = ""  # https://serpapi.com
SERPAPI_ADVANCED_SEARCH = {
    "location": "United States"
}   # additional params for google search
SERPAPI_LOT_NUMBER_REGEX = r"(?:Lot number|лот номером|lot number id)[\s:]*([0-9]+)"    # regex to find lot number in url preview


# updater
UPDATER_DELAY = 60     # affect searching new cars and checking old ones


# logs
LOGS_LEVEL = "DEBUG"


# resources
RESOURCES_DIR = "resources"
LOGS_DIR = os.path.join(RESOURCES_DIR, "logs")
LOCALES_DIR = os.path.join(RESOURCES_DIR, "locales")
