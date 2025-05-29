import sys
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Book, UserBook
from base import clean_description
from connection import engine, create_tables
import random
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

urls = {
    "Современная зарубежная литература": "https://www.livelib.ru/genre/Современная-зарубежная-литература",
    "Зарубежная классика": "https://www.livelib.ru/genre/Зарубежная-классика",
    "Зарубежные детективы": "https://www.livelib.ru/genre/Зарубежные-детективы",
    "Фэнтези": "https://www.livelib.ru/genre/Фэнтези",
    "Приключения": "https://www.livelib.ru/genre/Приключения"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

async def fetch(session, url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.livelib.ru/"
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
                isbn, publication_year, publisher = None, None, None

                for row in rows:
                    label = row.find("td", class_="book-item-edition__col1").text.strip()
                    value = row.find_all("td")[1].text.strip()
                    if label == "ISBN:":
                        isbn = value
                    elif label == "Год издания:":
                        publication_year = int(value)
                    elif label == "Издательство:":
                        publisher = value

                if publisher:
                    publisher = publisher.replace('\xa0', ' ').replace('\r', '').replace('\n', '').strip()
                    publisher = ', '.join(part.strip() for part in publisher.split(','))

                description_div = item.find("div", class_="book-item__text")
                description = description_div.get_text(separator="\n").strip() if description_div else None
                description = clean_description(description) if description else None

                book_data = {
                    "title": title,
                    "author": author,
                    "genre": genre_name,
                    "isbn": isbn,
                    "publication_year": publication_year,
                    "condition": "unknown",
                    "description": description
                }

                books.append(book_data)
            except Exception as e:
                print(f"Ошибка при парсинге книги: {e}")
                continue
    except Exception as e:
        print(f"Ошибка при получении HTML: {e}")

    return books

async def save_books_to_db(books, user_id=1):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        for book_data in books:
            existing_book = await session.exec(
                select(Book).where(
                    (Book.isbn == book_data["isbn"]) |
                    ((Book.title == book_data["title"]) & (Book.author == book_data["author"]))
                )
            ).first()

            if not existing_book:
                book = Book(**book_data)
                session.add(book)
                await session.flush()
                book_id = book.book_id
            else:
                book_id = existing_book.book_id

            user_book = UserBook(
                user_id=user_id,
                book_id=book_id,
                status="available",
                location="unknown"
            )
            session.add(user_book)

        await session.commit()

async def async_parse_and_save(session, url, genre, user_id=1):
    books = await parse_books_from_genre_page(session, url, genre)
    await save_books_to_db(books, user_id)
    print(f"[{genre}] Сохранено {len(books)} книг")

async def run_with_async():
    start_time = time.time()

    # Создаем таблицы перед парсингом
    await create_tables()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for genre, url in urls.items():
            tasks.append(async_parse_and_save(session, url, genre))

        await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Async time: {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    asyncio.run(run_with_async())