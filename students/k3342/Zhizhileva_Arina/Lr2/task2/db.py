import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.models import Book
from sqlmodel import Session
from base import parse_books_from_goodreads
from connection import engine


def parse_and_save(url: str, genre: str, max_books: int = 3):
    books_data = parse_books_from_goodreads(url, genre, max_books=max_books)

    with Session(engine) as session:
        for book_data in books_data:
            book = Book(
                title=book_data["title"],
                author=book_data["author"],
                genre=book_data["genre"],
                isbn=book_data["isbn"],
                published_in=book_data["published_in"],
                publisher=book_data["publisher"],
                description=book_data["description"]
            )
            session.add(book)

        session.commit()
        print(f"[{genre}] Сохранено {len(books_data)} книг")
