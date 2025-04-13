from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import UserBook, User, Book
from schemas.user_book import UserBookCreate, UserBookRead, UserBookUpdate
from api.dependencies import get_current_user

router = APIRouter(prefix="/user-books", tags=["user_books"])


@router.post("/", response_model=UserBookRead)
def create_user_book(
        user_book: UserBookCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Проверяем, что пользователь и книга существуют
    user = session.get(User, user_book.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    book = session.get(Book, user_book.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Проверяем, что у пользователя еще нет этой книги
    existing = session.exec(
        select(UserBook).where(
            (UserBook.user_id == user_book.user_id) &
            (UserBook.book_id == user_book.book_id)
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has this book")

    db_user_book = UserBook.from_orm(user_book)
    session.add(db_user_book)
    session.commit()
    session.refresh(db_user_book)
    return db_user_book


@router.get("/", response_model=List[UserBookRead])
def read_user_books(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    user_books = session.exec(select(UserBook).offset(skip).limit(limit)).all()
    return user_books


@router.get("/{user_book_id}", response_model=UserBookRead)
def read_user_book(user_book_id: int, session: Session = Depends(get_session)):
    user_book = session.get(UserBook, user_book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")
    return user_book


@router.patch("/{user_book_id}", response_model=UserBookRead)
def update_user_book(
        user_book_id: int,
        user_book: UserBookUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_user_book = session.get(UserBook, user_book_id)
    if not db_user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")

    # Проверяем, что текущий пользователь - владелец книги
    if db_user_book.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_book_data = user_book.dict(exclude_unset=True)
    for key, value in user_book_data.items():
        setattr(db_user_book, key, value)

    session.add(db_user_book)
    session.commit()
    session.refresh(db_user_book)
    return db_user_book


@router.delete("/{user_book_id}")
def delete_user_book(
        user_book_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    db_user_book = session.get(UserBook, user_book_id)
    if not db_user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")

    if db_user_book.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(db_user_book)
    session.commit()
    return {"ok": True}