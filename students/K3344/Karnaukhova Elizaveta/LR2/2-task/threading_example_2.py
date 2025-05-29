import random
import threading
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from sqlmodel import select
from models import *
from threading import Lock

DATABASE_URL = "postgresql://postgres:992327@localhost:8000/book_db"
# Создаем engine для каждого потока отдельно
engine = None
db_lock = Lock()  # Блокировка для работы с БД
SQLModel.metadata.create_all(create_engine(DATABASE_URL))

URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


def get_engine():
    """Создаем новый engine для каждого потока"""
    return create_engine(DATABASE_URL)


def parse_books(url: str) -> List[BookItem]:
    """Парсинг книг со страницы автора"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
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
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")
        return []


def save_books(books: List[BookItem]):
    """Сохранение книг в БД с блокировкой"""
    global engine
    if not books:
        return

    with db_lock:
        try:
            # Создаем engine при первом использовании в потоке
            if engine is None:
                engine = get_engine()

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
        except Exception as e:
            print(f"Ошибка при сохранении книг: {str(e)}")


def parse_and_save(url: str):
    """Функция для потока: парсинг и сохранение"""
    print(f"Начало парсинга {url}")
    try:
        books = parse_books(url)
        if books:
            save_books(books)
            print(f"Успешно сохранено {len(books)} книг с {url}")
        else:
            print(f"Не удалось получить книги с {url}")
    except Exception as e:
        print(f"Ошибка в потоке для {url}: {str(e)}")


def main():
    start_time = time.time()

    threads = []
    for url in URLS:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    main()

# Начало парсинга https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Начало парсинга https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Начало парсинга https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Успешно сохранено 20 книг с https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Успешно сохранено 20 книг с https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Успешно сохранено 20 книг с https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Общее время выполнения: 0.52 секунд