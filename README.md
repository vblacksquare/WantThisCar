# WantThisCar

## Overview
This project is a tool to search new cars from autoria with telegram interface.

### Setup (for linux Ubuntu)
1. Download python3.11
    

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    apt install python3.11-full


2. Create venv for project
    
    
    python3.11 -m venv venv
    venv/bin/activate

3. Install dependencies


    python -m pip install -r requirements.txt


3. Fill up config.py with your data
    
    
**Required**:
    
    BOT_TOKEN: your telegram bot token (via https://t.me/botfather)
    MONGODB_URI: your mongodb uri (info -> https://www.mongodb.com/community/forums/t/how-to-host-your-own-mongodb-server-without-using-hosting-providers/14435)
    SERPAPI_TOKEN: your serpapi token (register for token -> https://serpapi.com)

**Optional**:
    
    COMMANDS: list of telegram bot commands. Have to be filled with new ones to work correctly
    LANGUAGES: list of available locales for telegram bot interface 
    DEFAULT_LANGUAGE: default language if user's language isnt in LANGUAGES
    

5. Fill db with autoria categories

    
    python update_categories.py


### Usage
    
    python main.py
    
    OR in screen mode

    python main.py s


### Resources

    Locales are in resources/locales
    Logs are in resources/logs


### Tech details


#### Default functional (./parser module)

Basically it's working like this:

1. Search new car via private api of auto.ria with user's query
2. If car have bidfax link:
   1. Search for bidfax link preview in google search (because of cloudflare)
   2. Get lot number via description of preview
   3. Generate link to image on bid.cars of car on auction with the data
4. Save to db
5. Send user new car


#### Updating cars (./updater module)

To update cars data bot uses while loop with delay

#### Db

I often use my small interface over default motor lib to save some time. Of course it have a lot of minuses but it is not a big problem with small project like this.

**Example:**

    import typing
    from dtypes.db import method
    from dtypes.db import Example
    
    print(
        await Db().ex(
            method.FindOne(
                target=Example,
                name="test",
                key={"$in": [1, 2, 3]}
            )
        )
    )


**Output:**

    [Example(id="1"), Example(id="2") ...]

    
It uses jsonify module to transform from class to dict -> ./utils/jsonify.py

**Example:**
    
    from utils.jsonify import Jsonified

    class SmallExample(Jsonified):
        def init(
            self,
            test: str
        ):
            
            self.test = test

            sel.fields = ["test"]
    
    class Example(Jsonified):
        def init(
            self,
            name: str,
            key: int,
            small_example: SmallExample
        ):

            self.name = name
            self.key = key
            self.small_example = small_example
            
            self.invisible_field = None
            
            self.fields = ["name", "key", "small_example"]

    print(Example(name="test", key=1, small_example=SmallExample(test="hello")).to_dict())

**Output:**

    {
        "name": "test"
        "key": 1,
        "small_example": {
            "test": "hello"
        }
    }
