from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from models.models import Book, BookInfo
from models.default_models import BookDefault, BookInfoDefault
from models.public_models import BookPublic
from connection import get_session
from typing_extensions import TypedDict

book_router = APIRouter()

@book_router.get("/book_instance/{id}", response_model=BookPublic)
def get_book_instance(id: int, session=Depends(get_session)):
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@book_router.post("/book_instance")
def create_book(book: BookDefault, session=Depends(get_session)) -> TypedDict("Response", {"status": int, "created": Book}):
    book = Book.model_validate(book)
    session.add(book)
    session.commit()
    session.refresh(book)
    return {"status": 201, "created": book}
