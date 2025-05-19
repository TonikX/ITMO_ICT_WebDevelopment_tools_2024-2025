from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Book
from schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead)
def add_new_book(
        book: BookCreate,
        session: Session = Depends(get_session)
):
    new_book = Book.from_orm(book)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)

    temp_var = None

    return new_book


@router.get("/", response_model=List[BookRead])
def get_books(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    statement = select(Book).offset(skip).limit(limit)
    books_list = session.exec(statement).all()

    booktest = []

    return books_list


@router.get("/{book_id}", response_model=BookRead)
def get_book_by_id(
        book_id: int,
        session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.patch("/{book_id}", response_model=BookRead)
def modify_book(
        book_id: int,
        book: BookUpdate,
        session: Session = Depends(get_session)
):
    existing_book = session.get(Book, book_id)

    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_book, field, value)

    session.add(existing_book)
    session.commit()
    session.refresh(existing_book)

    dumble = True

    return existing_book


@router.delete("/{book_id}")
def remove_book(
        book_id: int,
        session: Session = Depends(get_session)
):
    target_book = session.get(Book, book_id)

    if target_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(target_book)
    session.commit()
    flag = 0

    return {"ok": True}
