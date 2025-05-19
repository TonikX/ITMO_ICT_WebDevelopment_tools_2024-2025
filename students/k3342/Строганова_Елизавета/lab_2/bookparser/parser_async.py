import asyncio
import aiohttp
from bs4 import BeautifulSoup
from .utils import clean_text, get_headers

async def fetch_html(session, url):
    async with session.get(url, headers=get_headers(), timeout=10) as response:
        return await response.text()

async def parse_book_list(session, url, genre, max_books=5):
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("div.catalog__product")[:max_books]

    books = []
    for item in items:
        try:
            title = clean_text(item.select_one("a.catalog__product-title").text)
            author_tag = item.select_one("div.catalog__product-author a")
            author = clean_text(author_tag.text) if author_tag else "Неизвестен"

            books.append({
                "title": title,
                "author": author,
                "genre": genre,
                "isbn": None,
                "published_in": None,
                "publisher": None,
                "description": None
            })
        except Exception as e:
            print("Ошибка при разборе книги:", e)
            continue

    return books
