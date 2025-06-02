import aiohttp
import requests


URLS = [
    "https://www.car.info/en-se/volkswagen",
    "https://www.car.info/en-se/toyota",
    "https://www.car.info/en-se/ford",
]


def sync_fetch_html(url: str):
    r = requests.get(url)
    return r.text


async def async_fetch_html(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

