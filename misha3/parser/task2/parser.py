import requests
import aiohttp
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/catalogue/category/books_1/index.html"


def parse_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for h3 in soup.select("h3 a"):
        title = h3.attrs.get("title", "").strip()
        if title:
            books.append(title)
    return books


def fetch_sync():
    r = requests.get(URL)
    return parse_html(r.text)


async def fetch_async():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            text = await r.text()
            return parse_html(text)