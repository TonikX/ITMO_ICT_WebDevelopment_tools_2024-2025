from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from ..models.BookItem import BookItem
from ..models.UserBook import UserBook
from ..models.UserProfile import UserProfile
from ..schemas.book import (
    BookItemCreate,
    BookItemRead,
    BookItemUpdate,
    UserBookCreate,
    UserBookRead
)
from ..db import get_session

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/search", response_model=List[BookItemRead])
def search_books(query: str, db: Session = Depends(get_session)):
    """Поиск книг по названию."""
    books = db.exec(select(BookItem).where(BookItem.title.contains(query))).all()
    if not books:
        raise HTTPException(status_code=404, detail="Книги не найдены")
    return books


# CRUD для BookItem (книг в системе)
@router.post("/", response_model=BookItemRead)
def create_book(book: BookItemCreate, db: Session = Depends(get_session)):
    db_book = BookItem.from_orm(book)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=List[BookItemRead])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    books = db.exec(select(BookItem).offset(skip).limit(limit)).all()
    return books


@router.get("/{book_id}", response_model=BookItemRead)
def read_book(book_id: int, db: Session = Depends(get_session)):
    book = db.get(BookItem, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookItemRead)
def update_book(book_id: int, book: BookItemUpdate, db: Session = Depends(get_session)):
    db_book = db.get(BookItem, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = book.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_session)):
    book = db.get(BookItem, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"ok": True}


@router.post("/{user_id}/library", response_model=UserBookRead)
def add_book_to_library(
        user_id: int,
        user_book: UserBookCreate,
        db: Session = Depends(get_session)
):
    # Находим профиль пользователя
    profile = db.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Проверяем существование книги
    book = db.get(BookItem, user_book.book_item_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Проверяем, не добавлена ли книга уже
    existing = db.exec(
        select(UserBook)
            .where(UserBook.user_profile_id == profile.id)
            .where(UserBook.book_item_id == user_book.book_item_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Book already in library")

    # Создаем связь между пользователем и книгой
    db_user_book = UserBook(
        user_profile_id=profile.id,
        book_item_id=user_book.book_item_id,
        status=user_book.status
    )
    db.add(db_user_book)
    db.commit()
    db.refresh(db_user_book)

    # Возвращаем результат
    return UserBookRead(
        book_item=BookItemRead.model_validate(book),
        user_profile_id=profile.id,
        status=db_user_book.status
    )


@router.get("/{user_id}/library", response_model=List[UserBookRead])
def get_user_library(user_id: int, db: Session = Depends(get_session)):
    profile = db.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_books = db.exec(
        select(UserBook)
            .where(UserBook.user_profile_id == profile.id)
            .join(BookItem)
    ).all()

    return [
        UserBookRead(
            book_item=BookItemRead.model_validate(ub.book_item),
            user_profile_id=profile.id,
            status=ub.status
        )
        for ub in user_books
    ]


@router.delete("/{user_id}/library/{book_id}")
def remove_book_from_library(
        user_id: int,
        book_id: int,
        db: Session = Depends(get_session)
):
    profile = db.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_book = db.exec(
        select(UserBook)
            .where(UserBook.user_profile_id == profile.id)
            .where(UserBook.book_item_id == book_id)
    ).first()

    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in library")

    db.delete(user_book)
    db.commit()
    return {"ok": True}
