from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from models import Book, BookCreate, Library
from connection import get_session

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/book")
def add_book(book: BookCreate, session=Depends(get_session)) -> TypedDict('Response',
                                                                          {"status": int, "data": BookCreate}):
    book = Book.model_validate(book)
    session.add(book)
    session.commit()
    session.refresh(book)
    return {"status": 200, "data": book}


@router.get("/books_list")
def books_list(session=Depends(get_session)):
    return session.exec(select(Book)).all()


@router.get("/book/{book_id}")
def book_get(book_id: int, session=Depends(get_session)) -> Book:
    return session.exec(select(Book).where(Book.id == book_id)).first()


@router.get("/user/{user_id}/books", response_model=List[Book])
def get_books_by_user(user_id: int, session=Depends(get_session)):
    library_entries = session.exec(
        select(Library).where(Library.user_id == user_id)
    ).all()

    if not library_entries:
        raise HTTPException(status_code=404, detail="User has no books")

    books = [entry.book for entry in library_entries if entry.book]

    return books


@router.get("/user/{user_id}/books/available", response_model=List[Book])
def get_available_books_by_user(user_id: int, session=Depends(get_session)):
    library_entries = session.exec(
        select(Library).where(
            (Library.user_id == user_id) &
            (Library.book_status == "Available")
        )
    ).all()

    books = [entry.book for entry in library_entries if entry.book]
    return books


@router.get("/search")
def search_books(title: str = None, author: str = None, session=Depends(get_session)):
    query = select(Book)
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    return session.exec(query).all()


@router.patch("/book{book_id}")
def book_update(book_id: int, book: BookCreate, session=Depends(get_session)) -> BookCreate:
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = book.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/book/delete{book_id}")
def book_delete(book_id: int, session=Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"ok": True}
