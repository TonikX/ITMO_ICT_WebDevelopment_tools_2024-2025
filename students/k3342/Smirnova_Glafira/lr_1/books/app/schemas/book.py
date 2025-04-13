from sqlmodel import SQLModel
from typing import List


class BookBase(SQLModel):
    """Базовая схема книги"""
    name: str
    author: str
    year: int
    publisher: str

class BookCreate(BookBase):
    """Схема для добавления книги"""
    pass

class BookRead(BookBase):
    """Схема для отображения книги"""
    id: int

class BookUpdate(SQLModel):
    """Схема для обновления книги"""
    name: str | None = None
    author: str | None = None
    year: int | None = None
    publisher: str | None = None

class BookFull(BookRead):
    genres: List["GenreRead"]

class BookGenresUpdate(SQLModel):
    """Схема для установки жанров книги (удаляет старые и добавляет новые)."""
    genre_ids: List[int]

class GenreRead(SQLModel):
    """Схема для возврата жанров."""
    id: int
    name: str