from typing import Optional

from books_lab2.task2.common.connection import get_session
from books_lab2.task2.common.models import Genre, Book


def get_or_create_genre(session, genre_name: str) -> Optional[int]:
    if not genre_name:
        return None

    genre = session.query(Genre).filter_by(name=genre_name).first()
    if not genre:
        genre = Genre(name=genre_name)
        session.add(genre)
        session.commit()
        session.refresh(genre)
    return genre.id

def save_books(books_data):
    with next(get_session()) as session:
        for data in books_data:
            genre_id = get_or_create_genre(session, data["genre_name"]) if data["genre_name"] else 1

            book = Book(
                title=data["title"],
                author=data["author"],
                description=data["description"],
                year=data["year"],
                genre_id=genre_id,
                owner_id=1
            )
            session.add(book)
        session.commit()
