from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Book, User
from schemas.book import BookCreate, BookRead, BookUpdate
from api.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead)
def create_book(
        book: BookCreate,
        session: Session = Depends(get_session)
):
    db_book = Book.from_orm(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.get("/", response_model=List[BookRead])
def read_books(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    books = session.exec(select(Book).offset(skip).limit(limit)).all()
    return books


@router.get("/{book_id}", response_model=BookRead)
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
        book_id: int,
        book: BookUpdate,
        session: Session = Depends(get_session),
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = book.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/{book_id}")
def delete_book(
        book_id: int,
        session: Session = Depends(get_session),
):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(db_book)
    session.commit()
    return {"ok": True}