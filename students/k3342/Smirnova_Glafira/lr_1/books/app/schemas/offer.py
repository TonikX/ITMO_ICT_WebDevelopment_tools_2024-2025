from enum import Enum

from sqlmodel import SQLModel

from app.schemas.book import BookFull, BookRead
from app.db.genres import DEFAULT_GENRES


class OfferUpdate(SQLModel):
    """Схема для обновления оффера."""
    comment: str | None = ""

class OfferCreate(OfferUpdate):
    """Схема для создания оффера."""
    book_id: int

class OfferShort(OfferCreate):
    """Схема для отображения оффера."""
    id: int
    created_at: str

class OfferFull(SQLModel):
    """Полная схема оффера (возвращается при запросе списка или одного оффера)."""
    id: int
    user_id: int
    comment: str | None = None
    book: BookFull
    created_at: str

class OfferInSwapList(SQLModel):
    id: int
    user_id: int
    book: BookRead

GenreEnum = Enum("GenreEnum", {genre.lower().replace(" ", "_"): genre for genre in DEFAULT_GENRES})

class SortOrder(str, Enum):
    asc = "date_asc"
    desc = "date_desc"

class OfferFilter(SQLModel):
    """Фильтры для поиска офферов."""
    name: str | None = None
    author: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    user_id: int | None = None
    genre: GenreEnum | None = None
    sort_order: SortOrder | None = SortOrder.desc