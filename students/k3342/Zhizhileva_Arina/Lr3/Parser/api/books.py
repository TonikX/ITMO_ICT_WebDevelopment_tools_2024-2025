from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from models import Book, User
from schemas.book import BookCreate, BookRead, BookUpdate
from api.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookRead)
async def create_book(
        book: BookCreate,
        session: AsyncSession = Depends(get_session)
):
    db_book = Book.from_orm(book)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookRead])
async def read_books(
        skip: int = 0,
        limit: int = 100,
        session: AsyncSession = Depends(get_session)
):
    books = await session.exec(select(Book).offset(skip).limit(limit)).all()
    return books

@router.get("/{book_id}", response_model=BookRead)
async def read_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.patch("/{book_id}", response_model=BookRead)
async def update_book(
        book_id: int,
        book: BookUpdate,
        session: AsyncSession = Depends(get_session),
):
    db_book = await session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = book.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_session),
):
    db_book = await session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    await session.delete(db_book)
    await session.commit()
    return {"ok": True}