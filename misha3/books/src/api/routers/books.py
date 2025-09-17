from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.api.controllers.book_controller import (
    create_book, get_books, get_book, update_book, delete_book
)
from pg.schemas.schema import BookCreate, BookRead
from database import get_session

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead)
def api_create_book(book_in: BookCreate, session: Session = Depends(get_session)):
    return create_book(session, book_in)


@router.get("/", response_model=List[BookRead])
def api_get_books(session: Session = Depends(get_session)):
    return get_books(session)


@router.get("/{book_id}", response_model=BookRead)
def api_get_book(book_id: int, session: Session = Depends(get_session)):
    return get_book(session, book_id)


@router.put("/{book_id}", response_model=BookRead)
def api_update_book(book_id: int, book_in: BookCreate, session: Session = Depends(get_session)):
    return update_book(session, book_in, book_id)


@router.delete("/{book_id}")
def api_delete_book(book_id: int, session: Session = Depends(get_session)):
    return delete_book(session, book_id)
