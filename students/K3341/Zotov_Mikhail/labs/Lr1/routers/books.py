from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..connection import get_session
from ..models import Book, BookRead, BookUpdate, BookCreate

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.get("/", response_model=list[BookRead])
def read_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books


@router.get("/{book_id}", response_model=BookRead)
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_data: BookUpdate, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_data.model_dump(exclude_unset=True).items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"ok": True}