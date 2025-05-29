import multiprocessing
from multiprocessing import Pool
import random
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from sqlmodel import select
from models import *

DATABASE_URL = "postgresql://postgres:992327@localhost:8000/book_db"


def get_engine():
    """Создаем новый engine для каждого процесса"""
    return create_engine(DATABASE_URL)


URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


def parse_books(url: str) -> List[BookItem]:
    """Парсинг книг со страницы автора"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    author = soup.find('div', class_='author-header__name').text.strip()

    books = []
    for book_item in soup.find_all('div', class_='book-item__inner'):
        title = book_item.find('a', class_='book-item__title').text.strip()
        description = book_item.find('p')
        description = ".".join(description.text.strip().split(".")[:3]) + "." if description else None

        books.append(BookItem(
            title=title,
            author=author,
            description=description
        ))

    return books


def save_books(books: List[BookItem], engine):
    """Сохранение книг в БД"""
    with Session(engine) as session:
        # Получаем список всех пользователей
        users = session.exec(select(UserProfile)).all()
        if not users:
            print("Нет пользователей в базе данных. Сначала создайте пользователей.")
            return

        for book in books:
            # Создаем книгу
            session.add(book)
            session.commit()
            session.refresh(book)

            # Связываем книгу со случайным пользователем
            random_user = random.choice(users)
            user_book = UserBook(
                user_profile_id=random_user.id,
                book_item_id=book.id,
                status=BookStatus.AVAILABLE
            )
            session.add(user_book)

        session.commit()


def parse_and_save(url: str):
    """Функция для процесса: парсинг и сохранение"""
    print(f"Парсинг {url}")
    try:
        # Создаем engine внутри процесса
        engine = get_engine()
        books = parse_books(url)
        save_books(books, engine)
        print(f"Сохранено {len(books)} книг с {url}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {str(e)}")


def main():
    start_time = time.time()

    # Создаем таблицы в основном процессе
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

    # Запускаем процессы
    with Pool(processes=min(len(URLS), multiprocessing.cpu_count())) as pool:
        pool.map(parse_and_save, URLS)

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

# Парсинг https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Парсинг https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Парсинг https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Сохранено 20 книг с https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Сохранено 20 книг с https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Сохранено 20 книг с https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Общее время выполнения: 1.26 секунд