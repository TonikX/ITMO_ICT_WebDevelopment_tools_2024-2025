from typing import List
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException

from src.models import Book
from pg.schemas.schema import BookCreate, BookRead


def create_book(session: Session, book_in: BookCreate) -> BookRead:
    book = Book(**book_in.dict())
    session.add(book)
    session.commit()
    session.refresh(book)
    return BookRead.from_orm(book)


def get_books(session: Session) -> List[BookRead]:
    books = session.exec(select(Book)).all()
    return [BookRead.from_orm(b) for b in books]


def get_book(session: Session, book_id: int) -> BookRead:
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookRead.from_orm(book)


def update_book(session: Session, book_id: int, book_in: BookCreate) -> BookRead:
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_in.dict().items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return BookRead.from_orm(book)


def delete_book(session: Session, book_id: int):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"detail": f"Book {book_id} deleted"}
