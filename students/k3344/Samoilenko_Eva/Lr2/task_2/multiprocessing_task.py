import multiprocessing
from multiprocessing import Pool
import random
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from sqlmodel import select
from models import *


DATABASE_URL = "postgresql://postgres:superuser@localhost:5432/bookcrossing_db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


def parse_books(url: str) -> List[BookBase]:
    """Парсинг книг со страницы автора"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    author = soup.find('div', class_='author-header__name').text.strip()

    books = []
    for book_item in soup.find_all('div', class_='book-item__inner'):
        title = book_item.find('a', class_='book-item__title').text.strip()
        description = book_item.find('p')
        description = ".".join(description.text.strip().split(".")[:3]) + "." if description else \
            None

        books.append(BookBase(
            title=title,
            author=author,
            description=description,
        ))

    return books


# def save_books(books: List[BookBase]):
#     """Сохранение книг в БД"""
#     with Session(engine) as session:
#         for book in books:
#             profile_library_id = random.randint(1, 5)
#             library = session.exec(
#                 select(ProfileLibrary)
#                 .where(ProfileLibrary.id == profile_library_id)).first()
#             db_book = Book(**book.model_dump(), profile_library_id=library.id)
#             session.add(db_book)
#         session.commit()


def parse_and_save(url: str):
    """Функция для процесса: парсинг и сохранение"""
    print(f"Парсинг {url}")
    books = parse_books(url)

    # Каждый процесс должен иметь свое подключение к БД
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        for book in books:
            profile_library_id = random.randint(1, 5)
            library = session.exec(
                select(ProfileLibrary)
                .where(ProfileLibrary.id == profile_library_id)).first()
            db_book = Book(**book.model_dump(), profile_library_id=library.id)
            session.add(db_book)
        session.commit()

    print(f"Сохранено {len(books)} книг с {url}")


def main():
    start_time = time.time()

    with Pool(processes=len(URLS)) as pool:
        pool.map(parse_and_save, URLS)

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
