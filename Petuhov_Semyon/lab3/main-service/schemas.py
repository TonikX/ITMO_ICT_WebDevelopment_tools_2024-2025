from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel

# Повторяем enum-ы для схем, чтобы корректно сериализовать
class Genres(str, Enum):
    sci_fi = "Science Fiction"
    non_fi = "Non-fiction"
    Novel = "Novel"

class BookStatuses(str, Enum):
    available = "available"
    Ordered = "Ordered"
    Exchanged = "Exchanged"


class ParseRequest(BaseModel):
    url: str
    genre: str
# === User ===

class UserBase(SQLModel):
    username: str
    email: str
    about_me: Optional[str] = None

class UserCreate(UserBase):
    password: str  # При создании надо передавать plain password

class UserRead(UserBase):
    id: int
    created_at: Optional[str] = None

    class Config:
        orm_mode = True


# === Book ===

class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    published_year: int

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    id: int

    class Config:
        orm_mode = True


# === UserBook ===

class UserBookBase(SQLModel):
    user_id: int
    book_id: int
    status: BookStatuses

class UserBookRead(UserBookBase):
    id: int
    user: Optional[UserRead] = None
    book: Optional[BookRead] = None

    class Config:
        orm_mode = True

class UserBookCreate(UserBookBase):
    pass


# === Offer ===

class OfferBase(SQLModel):
    sender_id: int
    receiver_id: int
    sender_book_id: int
    receiver_book_id: int
    sender_confirm: bool = False
    receiver_confirm: bool = False
    status: str = "pending"

class OfferCreate(OfferBase):
    pass  # Можно добавить валидации по желанию

class OfferRead(OfferBase):
    id: int
    created_at: Optional[str] = None
    sender: Optional[UserRead] = None
    receiver: Optional[UserRead] = None
    sender_book: Optional[UserBookRead] = None
    receiver_book: Optional[UserBookRead] = None
    # Можно добавить exchange, если нужно
    # exchange: Optional["ExchangeRead"] = None

    class Config:
        orm_mode = True


# === Exchange ===

class ExchangeBase(SQLModel):
    offer_id: int

class ExchangeCreate(ExchangeBase):
    pass

class ExchangeRead(ExchangeBase):
    id: int
    exchange_date: Optional[str] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    username: str

    class Config:
        orm_mode = True


# Только title и author из Book
class BookSimpleResponse(BaseModel):
    title: str
    author: str

    class Config:
        orm_mode = True


# Только id и вложенный book с title + author
class UserBookResponse(BaseModel):
    id: int
    book: BookSimpleResponse

    class Config:
        orm_mode = True


# Финальная упрощённая схема Offer
class OfferResponse(BaseModel):
    id: int
    sender: UserResponse
    receiver: UserResponse
    sender_book: UserBookResponse
    receiver_book: UserBookResponse
    sender_confirm: bool
    receiver_confirm: bool
    status: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ExchangeResponse(BaseModel):
    id: int
    exchange_date: Optional[datetime] = None
    offer: OfferResponse

    class Config:
        orm_mode = True
