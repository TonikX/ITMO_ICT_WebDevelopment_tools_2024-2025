# api/schemas/book_schemas.py
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from api.models.models import Status


class BookCreate(BaseModel):
    user_id: int
    title: str
    author: str
    description: str
    status: Status = Status.available
    genre_ids: Optional[List[int]] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    user_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    genre_ids: Optional[List[int]] = None


# Для ответа можно вернуть список жанров (с id и названием)
class GenreForBookResponse(BaseModel):
    id: int
    name: str


class BookResponse(BaseModel):
    id: int
    user_id: int
    title: str
    author: str
    description: str
    status: Status
    genres: List[GenreForBookResponse] = []
