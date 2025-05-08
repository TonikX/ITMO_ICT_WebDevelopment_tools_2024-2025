import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session
from models.models import Book
from base import clean_description
from connection import engine
import random
import time

urls = {
    "Современная зарубежная литература": "https://www.livelib.ru/genre/Современная-зарубежная-литература",
    "Зарубежная классика": "https://www.livelib.ru/genre/Зарубежная-классика",
    "Зарубежные детективы": "https://www.livelib.ru/genre/Зарубежные-детективы",
    "Фэнтези": "https://www.livelib.ru/genre/Фэнтези",
    "Приключения": "https://www.livelib.ru/genre/Приключения"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)..."
]


async def fetch(session, url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "...",
        "Accept-Language": "...",
        "Referer": "..."
    }
    async with session.get(url, headers=headers, timeout=10) as response:
        return await response.text()


async def parse_books_from_genre_page(session, url, genre_name, max_books=3):
    books = []

    try:
        html = await fetch(session, url)
        await asyncio.sleep(random.uniform(1.5, 3.0))
        soup = BeautifulSoup(html, "html.parser")
        book_items = soup.select("li[class*=book-item__item]")[:max_books]

        for item in book_items:
            try:
                title_tag = item.find("a", class_="book-item__title")
                author_tag = item.find("a", class_="book-item__author")
                if not title_tag or not author_tag:
                    continue

                title = title_tag.text.strip()
                author = author_tag.text.strip()

                info_table = item.find("table", class_="book-item-edition")
                rows = info_table.find_all("tr") if info_table else []
                isbn, published_in, publisher = None, None, None

                for row in rows:
                    label = row.find("td", class_="book-item-edition__col1").text.strip()
                    value = row.find_all("td")[1].text.strip()
                    if label == "ISBN:":
                        isbn = value
                    elif label == "Год издания:":
                        published_in = int(value)
                    elif label == "Издательство:":
                        publisher = value

                if publisher:
                    publisher = publisher.replace('\xa0', ' ').replace('\r', '').replace('\n', '').strip()
                    publisher = ', '.join(part.strip() for part in publisher.split(','))

                description_div = item.find("div", class_="book-item__text")
                description = description_div.get_text(separator="\n").strip() if description_div else None
                description = clean_description(description)

                book_data = {
                    "title": title,
                    "author": author,
                    "genre": genre_name,
                    "isbn": isbn,
                    "published_in": published_in,
                    "publisher": publisher,
                    "description": description
                }

                books.append(book_data)
            except Exception as e:
                print("Ошибка при парсинге книги:", e)
                continue
    except Exception as e:
        print(f"Ошибка при получении HTML: {e}")

    return books


def save_books_to_db(books):
    with Session(engine) as session:
        for book_data in books:
            book = Book(**book_data)
            session.add(book)
        session.commit()


async def async_parse_and_save(session, url, genre):
    books = await parse_books_from_genre_page(session, url, genre)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, save_books_to_db, books)
    print(f"[{genre}] Сохранено {len(books)} книг")


async def run_with_async():
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for genre, url in urls.items():
            tasks.append(async_parse_and_save(session, url, genre))

        await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Async time: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    asyncio.run(run_with_async())
