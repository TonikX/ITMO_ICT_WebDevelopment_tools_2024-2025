from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import select
from typing_extensions import TypedDict

from models import Book, BookCreate, Library, LibraryRead
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


@router.get("/books/search", response_model=List[LibraryRead])
def search_book_in_libraries(
        query: str = Query(..., min_length=1),
        session=Depends(get_session)
):
    stmt = (
        select(Library)
        .join(Library.book)
        .join(Library.user)
        .where(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%"))
        )
        .options(selectinload(Library.book), selectinload(Library.user))
    )
    results = session.exec(stmt).all()
    if not results:
        raise HTTPException(status_code=404, detail="No books found matching the query")

    return results


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
