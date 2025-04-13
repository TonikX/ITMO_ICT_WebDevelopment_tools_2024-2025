from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.models import Book, Ownership, Genre, BookGenre
from app.schemas.book import BookCreate, BookUpdate, BookGenresUpdate


def add_book(book_create: BookCreate, user_id: int, session: Session) -> Book:
    """Добавляет книгу и создаёт владение."""
    book = Book.model_validate(book_create)
    session.add(book)
    session.commit()
    session.refresh(book)

    ownership = Ownership(user_id=user_id, book_id=book.id)
    session.add(ownership)
    session.commit()

    return book

def edit_book(book_id: int, book_update: BookUpdate, session: Session):
    """Обновляет книгу, если пользователь - её первый владелец."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book_update.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    session.commit()
    session.refresh(book)

    return book

def remove_book(book_id: int, session: Session):
    """Удаляет книгу и владение, если пользователь - первый владелец."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()

def remove_ownership(book_id: int, user_id: int, session: Session):
    """Удаляет владение книгой (сама книга остаётся в системе)."""
    statement = select(Ownership).where(
        (Ownership.book_id == book_id) & (Ownership.user_id == user_id) & (Ownership.is_current == True)
    )
    ownership = session.exec(statement).first()

    if not ownership:
        raise HTTPException(status_code=404, detail="Ownership not found or already removed")

    session.delete(ownership)
    session.commit()


def set_book_genres(book_id: int, genres_update: BookGenresUpdate, session: Session):
    """Устанавливает список жанров для книги: удаляет старые, добавляет новые."""

    statement = select(Genre).where(Genre.id.in_(genres_update.genre_ids))
    existing_genre_ids = {g.id for g in session.exec(statement).all()}

    missing_genres = set(genres_update.genre_ids) - existing_genre_ids
    if missing_genres:
        raise HTTPException(
            status_code=400,
            detail=f"Genres not found: {missing_genres}"
        )

    statement = select(BookGenre).where(BookGenre.book_id == book_id)
    existing_book_genres = {bg.genre_id for bg in session.exec(statement).all()}

    genres_to_remove = existing_book_genres - existing_genre_ids
    genres_to_add = existing_genre_ids - existing_book_genres

    if genres_to_remove:
        statement = select(BookGenre).where(
            (BookGenre.book_id == book_id) & (BookGenre.genre_id.in_(genres_to_remove))
        )
        for bg in session.exec(statement).all():
            session.delete(bg)

    new_genres = [BookGenre(book_id=book_id, genre_id=gid) for gid in genres_to_add]
    session.add_all(new_genres)

    session.commit()


def get_user_books(user_id: int, session: Session) -> list[Book]:
    """Возвращает список книг, которыми пользователь владеет в данный момент."""

    statement = select(Ownership).where((Ownership.user_id == user_id) & Ownership.is_current)
    book_ids = [row.book_id for row in session.exec(statement).all()]

    if not book_ids:
        return []

    statement = select(Book).where(Book.id.in_(book_ids))
    books = session.exec(statement).all()

    return books