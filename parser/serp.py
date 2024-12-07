
import aiohttp
import re

from loguru import logger

from config import SERPAPI_ROOT, SERPAPI_TOKEN, SERPAPI_ADVANCED_SEARCH, SERPAPI_LOT_NUMBER_REGEX


async def find_lot_number(bidfax_link: str) -> str | None:
    """
    Function to search bidfax preview at google search using external api.
    """

    data = None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=SERPAPI_ROOT,
                headers={
                  'X-API-KEY': SERPAPI_TOKEN,
                  'Content-Type': 'application/json'
                },
                json={
                    "q": bidfax_link,
                    **SERPAPI_ADVANCED_SEARCH
                }
            ) as resp:
                logger.debug(f"Got resposne -> {resp}")

                data = await resp.json()

    except Exception as err:
        logger.exception(err)

    if not data:
        return None

    for result in data["organic"]:
        snippet = result["snippet"]

        match = re.search(SERPAPI_LOT_NUMBER_REGEX, snippet)

        if match:
            return match.group(1)
