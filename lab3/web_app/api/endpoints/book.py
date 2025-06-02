from typing import List
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import select, delete
from api.models.connection import get_session
from api.models.models import Book, BookGenre, Genre
from api.schemas.book_schemas import BookCreate, BookResponse, BookUpdate, GenreForBookResponse

book_router = APIRouter()


@book_router.post("/book_create", response_model=BookResponse)
def book_create(book_data: BookCreate, session=Depends(get_session)):
    new_book = Book(
        user_id=book_data.user_id,
        title=book_data.title,
        author=book_data.author,
        description=book_data.description,
        status=book_data.status
    )
    session.add(new_book)
    session.commit()
    session.refresh(new_book)

    if book_data.genre_ids:
        for genre_id in book_data.genre_ids:
            genre = session.get(Genre, genre_id)
            if not genre:
                raise HTTPException(status_code=404, detail=f"Genre with id {genre_id} not found")
            session.add(BookGenre(book_id=new_book.id, genre_id=genre_id))
        session.commit()
        session.refresh(new_book)


    new_book.genres = session.exec(
        select(Genre).join(BookGenre, Genre.id == BookGenre.genre_id).where(BookGenre.book_id == new_book.id)
    ).all()

    return new_book


@book_router.patch("/book_patch/{book_id}", response_model=BookResponse)
def book_patch(book_id: int, book_update: BookUpdate, session=Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.dict(exclude_unset=True)


    if "genre_ids" in update_data:
        new_genre_ids = update_data.pop("genre_ids")

        session.exec(delete(BookGenre).where(BookGenre.book_id == book_id))

        if new_genre_ids:
            for genre_id in new_genre_ids:
                genre = session.get(Genre, genre_id)
                if not genre:
                    raise HTTPException(status_code=404, detail=f"Genre with id {genre_id} not found")
                session.add(BookGenre(book_id=book_id, genre_id=genre_id))

    for key, value in update_data.items():
        setattr(db_book, key, value)

    session.commit()
    session.refresh(db_book)


    db_book.genres = session.exec(
        select(Genre).join(BookGenre, Genre.id == BookGenre.genre_id).where(BookGenre.book_id == db_book.id)
    ).all()

    return db_book


@book_router.get("/books_get", response_model=List[BookResponse])
def books_get(session=Depends(get_session)):
    books = session.exec(select(Book)).all()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")

    for book in books:
        book.genres = session.exec(
            select(Genre).join(BookGenre, Genre.id == BookGenre.genre_id).where(BookGenre.book_id == book.id)
        ).all()
    return books


@book_router.get("/book_get/{book_id}", response_model=BookResponse)
def book_get(book_id: int, session=Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.genres = session.exec(
        select(Genre).join(BookGenre, Genre.id == BookGenre.genre_id).where(BookGenre.book_id == book.id)
    ).all()
    return book


@book_router.delete("/book_delete/{book_id}")
def book_delete(book_id: int, session=Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(db_book)
    session.commit()
    return {"ok": True}
