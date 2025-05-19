from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import UserBook, User, Book
from schemas.user_book import UserBookCreate, UserBookRead, UserBookUpdate
from api.dependencies import get_current_user

router = APIRouter(prefix="/user-books", tags=["user_books"])


@router.post("/", response_model=UserBookRead)
def add_user_book(
        user_book_data: UserBookCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    user = session.get(User, user_book_data.user_id)
    if not user:
        raise HTTPException(404, "User not found")

    book = session.get(Book, user_book_data.book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    exists = session.exec(
        select(UserBook).where(
            (UserBook.user_id == user_book_data.user_id) &
            (UserBook.book_id == user_book_data.book_id)
        )
    ).first()
    if exists:
        raise HTTPException(400, "User already owns this book")

    new_user_book = UserBook.from_orm(user_book_data)
    session.add(new_user_book)
    session.commit()
    session.refresh(new_user_book)
    return new_user_book


@router.get("/", response_model=List[UserBookRead])
def list_user_books(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    user_books = session.exec(select(UserBook).offset(skip).limit(limit)).all()
    return user_books


@router.get("/{user_book_id}", response_model=UserBookRead)
def get_user_book(user_book_id: int, session: Session = Depends(get_session)):
    user_book = session.get(UserBook, user_book_id)
    if not user_book:
        raise HTTPException(404, "UserBook not found")
    return user_book


@router.patch("/{user_book_id}", response_model=UserBookRead)
def modify_user_book(
        user_book_id: int,
        user_book_data: UserBookUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_user_book = session.get(UserBook, user_book_id)
    if not db_user_book:
        raise HTTPException(404, "UserBook not found")

    if db_user_book.user_id != current_user.user_id:
        raise HTTPException(403, "Permission denied")

    update_data = user_book_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user_book, key, value)

    session.add(db_user_book)
    session.commit()
    session.refresh(db_user_book)
    return db_user_book


@router.delete("/{user_book_id}")
def remove_user_book(
        user_book_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_user_book = session.get(UserBook, user_book_id)
    if not db_user_book:
        raise HTTPException(404, "UserBook not found")

    if db_user_book.user_id != current_user.user_id:
        raise HTTPException(403, "Permission denied")

    session.delete(db_user_book)
    session.commit()
    return {"ok": True}
