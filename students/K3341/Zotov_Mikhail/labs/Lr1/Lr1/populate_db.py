import os
from datetime import datetime
from enum import Enum

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session, select

# Импортируем все ваши модели (как в вашем коде)
from models import *

# Создаем движок SQLModel (используйте свою строку подключения)
load_dotenv()
db = os.getenv("BOOKCROSSING_DB")
engine = create_engine(db, echo=True)

# Создаем таблицы
SQLModel.metadata.create_all(engine)

# Функция для заполнения БД тестовыми данными
def populate_test_data():
    with Session(engine) as session:
        # Создаем жанры
        genres = [
            Genre(name="Фантастика"),
            Genre(name="Фэнтези"),
            Genre(name="Детектив"),
            Genre(name="Роман"),
            Genre(name="Научная литература"),
        ]
        session.add_all(genres)
        session.commit()  # Фиксируем, чтобы получить ID жанров

        # Создаем книги
        books = [
            Book(
                title="Властелин колец",
                author="Дж. Р. Р. Толкин",
                description="Эпическая фэнтезийная сага",
                isbn="978-5-17-080217-4",
            ),
            Book(
                title="1984",
                author="Джордж Оруэлл",
                description="Антиутопический роман",
                isbn="978-5-17-090640-7",
            ),
            Book(
                title="Убийство в Восточном экспрессе",
                author="Агата Кристи",
                description="Знаменитый детектив",
                isbn="978-5-699-90541-5",
            ),
            Book(
                title="Гарри Поттер и философский камень",
                author="Дж. К. Роулинг",
                description="Первая книга о Гарри Поттере",
                isbn="978-5-389-07435-4",
            ),
            Book(
                title="Краткая история времени",
                author="Стивен Хокинг",
                description="Научно-популярная книга о космологии",
                isbn="978-5-17-093981-8",
            ),
        ]
        session.add_all(books)
        session.commit()  # Фиксируем, чтобы получить ID книг

        # Получаем жанры и книги из базы
        fantasy_genre = session.exec(select(Genre).where(Genre.name == "Фэнтези")).first()
        scifi_genre = session.exec(select(Genre).where(Genre.name == "Фантастика")).first()
        detective_genre = session.exec(select(Genre).where(Genre.name == "Детектив")).first()
        novel_genre = session.exec(select(Genre).where(Genre.name == "Роман")).first()
        science_genre = session.exec(select(Genre).where(Genre.name == "Научная литература")).first()

        lotr = session.exec(select(Book).where(Book.title == "Властелин колец")).first()
        book1984 = session.exec(select(Book).where(Book.title == "1984")).first()
        murder = session.exec(select(Book).where(Book.title == "Убийство в Восточном экспрессе")).first()
        potter = session.exec(select(Book).where(Book.title == "Гарри Поттер и философский камень")).first()
        hawking = session.exec(select(Book).where(Book.title == "Краткая история времени")).first()

        # Связываем книги с жанрами
        book_genres = [
            BookGenre(book_id=lotr.id, genre_id=fantasy_genre.id),
            BookGenre(book_id=book1984.id, genre_id=scifi_genre.id),
            BookGenre(book_id=book1984.id, genre_id=novel_genre.id),
            BookGenre(book_id=murder.id, genre_id=detective_genre.id),
            BookGenre(book_id=potter.id, genre_id=scifi_genre.id),
            BookGenre(book_id=potter.id, genre_id=fantasy_genre.id),
            BookGenre(book_id=hawking.id, genre_id=science_genre.id),
        ]
        session.add_all(book_genres)
        session.commit()

        # Создаем пользователей
        users = [
            User(
                username="ivan_ivanov",
                email="ivan@example.com",
                bio="Люблю читать фантастику",
                hashed_password="hashed_password_1",
            ),
            User(
                username="anna_smith",
                email="anna@example.com",
                bio="Коллекционирую детективы",
                hashed_password="hashed_password_2",
            ),
            User(
                username="book_lover",
                email="book@example.com",
                bio="Читаю все подряд",
                hashed_password="hashed_password_3",
            ),
        ]
        session.add_all(users)
        session.commit()

        # Получаем пользователей из базы
        ivan = session.exec(select(User).where(User.username == "ivan_ivanov")).first()
        anna = session.exec(select(User).where(User.username == "anna_smith")).first()
        lover = session.exec(select(User).where(User.username == "book_lover")).first()

        # Добавляем книги в библиотеки пользователей
        libraries = [
            Library(user_id=ivan.id, book_id=lotr.id, is_available=True),
            Library(user_id=ivan.id, book_id=book1984.id, is_available=False),
            Library(user_id=anna.id, book_id=murder.id, is_available=True),
            Library(user_id=anna.id, book_id=potter.id, is_available=True),
            Library(user_id=lover.id, book_id=hawking.id, is_available=True),
            Library(user_id=lover.id, book_id=lotr.id, is_available=True),
        ]
        session.add_all(libraries)
        session.commit()

        # Создаем запросы на обмен
        exchange_requests = [
            ExchangeRequest(
                requester_id=ivan.id,
                owner_id=anna.id,
                requested_book_id=murder.id,
                offered_book_id=lotr.id,
                status=StatusExchangeRequest.pending,
                created_at=datetime(2023, 5, 1),
            ),
            ExchangeRequest(
                requester_id=lover.id,
                owner_id=ivan.id,
                requested_book_id=book1984.id,
                offered_book_id=hawking.id,
                status=StatusExchangeRequest.accepted,
                created_at=datetime(2023, 5, 5),
            ),
        ]
        session.add_all(exchange_requests)
        session.commit()

        print("Тестовые данные успешно добавлены!")

# Вызываем функцию для заполнения БД
if __name__ == "__main__":
    populate_test_data()