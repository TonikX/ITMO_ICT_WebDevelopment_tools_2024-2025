from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from db import get_session
from models import Book as BookModel
from schemas.book import Book as BookSchema, BookCreate, BookUpdate

router = APIRouter()


@router.post("/books/", response_model=BookSchema)
def create_book(book: BookCreate, session: Session = Depends(get_session)) -> BookSchema:
    db_book = BookModel(**book.dict())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return BookSchema.from_orm(db_book)


@router.get("/books/{book_id}", response_model=BookSchema)
def read_book(book_id: int, session: Session = Depends(get_session)) -> BookSchema:
    db_book = session.get(BookModel, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookSchema.from_orm(db_book)


@router.get("/books/", response_model=List[BookSchema])
def read_books(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)) -> List[BookSchema]:
    db_books = session.query(BookModel).offset(skip).limit(limit).all()
    return [BookSchema.from_orm(book) for book in db_books]


@router.patch("/books/{book_id}", response_model=BookSchema)
def update_book(book_id: int, book: BookUpdate, session: Session = Depends(get_session)) -> BookSchema:
    db_book = session.get(BookModel, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return BookSchema.from_orm(db_book)


@router.delete("/books/{book_id}", response_model=BookSchema)
def delete_book(book_id: int, session: Session = Depends(get_session)) -> BookSchema:
    db_book = session.get(BookModel, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    response: BookSchema = BookSchema.from_orm(db_book)
    session.delete(db_book)
    session.commit()
    return response
