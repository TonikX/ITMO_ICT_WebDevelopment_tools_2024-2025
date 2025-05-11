from typing import List
from fastapi import HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import selectinload
from sqlmodel import select

from api.models.connection import get_session
from api.models.models import Book, BookGenre, Genre
from api.schemas.book_schemas import BookResponse

services_router = APIRouter()


@services_router.get("search_book", response_model=List[BookResponse])
def search_book(title: str = None, genres: List[str] = Query(None), session=Depends(get_session)):
    query = select(Book).where(Book.status == "Доступна")

    if title:
        query = query.where(Book.title.contains(title))
    if genres:
        subquery = (
            select(BookGenre.book_id)
            .join(Genre)
            .where(Genre.name.in_(genres))
            .group_by(BookGenre.book_id)
            .subquery()
        )

        query = query.where(Book.id.in_(subquery))

    return session.exec(query).all()
