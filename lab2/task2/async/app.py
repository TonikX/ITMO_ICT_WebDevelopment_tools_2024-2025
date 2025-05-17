import os
import sys
import time
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from urls import MAX_PAGES, url

load_dotenv()
DATABASE_URI = os.environ["DATABASE_URI"]


async def create_book_record(
    conn, title: str, author: str, isbn: str, description: str
) -> None:
    await conn.execute(
        """
        INSERT INTO books (title, author, isbn, description)
        VALUES ($1, $2, $3, $4)
        """,
        title,
        author,
        isbn,
        description,
    )


async def parse_and_save(session, pool, url: str):
    try:
        print(f"Fetching {url}...")
        async with session.get(url, timeout=5) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            book_items = soup.find_all("li", class_="book-item__item book-item--full")
            async with pool.acquire() as conn:
                for book in book_items:
                    title = book.find("a", class_="book-item__title")
                    author = book.find("a", class_="book-item__author")
                    isbn = book.find("table", class_="book-item-edition")
                    description = book.find("div", id="lenta-card__text-edition-full")
                    if description is None:
                        description = book.find(
                            "div", id="lenta-card__text-edition-escaped"
                        )
                    title_text = title.get_text(strip=True) if title else None
                    author_text = author.get_text(strip=True) if author else None
                    isbn_text = None
                    if isbn:
                        td = isbn.find("td", class_=None)
                        isbn_text = td.get_text(strip=True) if td else None
                    description_text = (
                        description.get_text(strip=True) if description else None
                    )
                    await create_book_record(
                        conn, title_text, author_text, isbn_text, description_text
                    )
    except Exception as e:
        print(f"Error fetching/parsing {url}: {e}")


async def main():
    urls_to_fetch = [url.format(page=i) for i in range(1, MAX_PAGES + 1)]
    t0 = time.perf_counter()
    pool = await asyncpg.create_pool(DATABASE_URI, min_size=2, max_size=10)
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, pool, u) for u in urls_to_fetch]
        await asyncio.gather(*tasks)
    await pool.close()
    t1 = time.perf_counter()
    print(f"Async: time = {t1 - t0:.2f} s")


if __name__ == "__main__":
    asyncio.run(main())
