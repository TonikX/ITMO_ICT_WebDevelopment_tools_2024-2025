from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel

from enums.book_status import BookStatus
from enums.genre import BookGenre

if TYPE_CHECKING:
    from schemas.exchange import Exchange


class BookBase(BaseModel):
    title: str
    author: str
    genre: BookGenre
    book_status: Optional[BookStatus] = BookStatus.available
    owner_comment: Optional[str] = None

    class Config:
        orm_mode = True


class BookCreate(BookBase):
    owner_id: int


class BookUpdate(BookBase):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[BookGenre] = None
    book_status: Optional[BookStatus] = None
    owner_comment: Optional[str] = None


class Book(BookBase):
    id: int
    owner_exchanges: List["Exchange"] = []
    requester_exchanges: List["Exchange"] = []

    class Config:
        orm_mode = True


class BookShort(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        orm_mode = True
