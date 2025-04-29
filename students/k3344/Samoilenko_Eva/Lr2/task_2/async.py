import asyncio
import random
from sqlmodel import select

import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from models import *


DATABASE_URL = "postgresql://postgres:superuser@localhost:5432/bookcrossing_db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def parse_books(url: str) -> List[BookBase]:
    """Асинхронный парсинг книг"""
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        author = soup.find('div', class_='author-header__name').text.strip()

        books = []
        for book_item in soup.find_all('div', class_='book-item__inner'):
            title = book_item.find('a', class_='book-item__title').text.strip()
            description = book_item.find('p')
            description = ".".join(description.text.strip().split(".")[:3]) + "." if description else None

            books.append(BookBase(
                title=title,
                author=author,
                description=description
            ))

        return books


async def save_books(books: List[BookBase]):
    """Асинхронное сохранение книг"""
    with Session(engine) as session:
        for book in books:
            profile_library_id = random.randint(1, 5)
            library = session.exec(
                select(ProfileLibrary)
                .where(ProfileLibrary.id == profile_library_id)).first()
            db_book = Book(**book.model_dump(), profile_library_id=library.id)
            session.add(db_book)
        session.commit()


async def parse_and_save(url: str):
    """Асинхронная задача"""
    print(f"Парсинг {url}")
    books = await parse_books(url)
    await save_books(books)
    print(f"Сохранено {len(books)} книг с {url}")


async def main():
    start_time = time.time()

    tasks = [parse_and_save(url) for url in URLS]
    await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
