from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import Book, BookCreate, BookUpdate, BookInfo, User
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[BookInfo])
def get_books(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)

    books = session.exec(
        select(Book).options(selectinload(Book.owner))
    ).all()
    return books


@router.get("/{book_id}", response_model=BookInfo)
def get_book(book_id: int, request: Request, session: Session = Depends(get_session)):
    get_current_user(request)

    book = session.exec(
        select(Book).where(Book.id == book_id).options(selectinload(Book.owner))
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/create", response_model=BookInfo)
def create_book(book: BookCreate, request: Request, session: Session = Depends(get_session)):
    user_data = get_current_user(request)
    user_id = int(user_data.get("id"))
    current_user = session.get(User, user_id)
    db_book = Book.model_validate(book)
    db_book.owner_id = current_user.id

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    full_book = session.exec(
        select(Book).where(Book.id == db_book.id).options(selectinload(Book.owner))
    ).first()

    return full_book


@router.patch("/update/{book_id}", response_model=BookInfo)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    request: Request,
    session: Session = Depends(get_session)
):
    db_book = session.get(Book, book_id)
    current_user = get_current_user(request)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if db_book.owner_id != int(current_user["id"]):
        raise HTTPException(status_code=403, detail="You can only update your own books")

    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None and value != "":
            setattr(db_book, field, value)

    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/delete/{book_id}")
def delete_book(book_id: int, request: Request, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    get_current_user(request)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"message": "Book deleted"}
