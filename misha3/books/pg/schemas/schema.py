from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlmodel import SQLModel


class Genres(str, Enum):
    sci_fi = "Science Fiction"
    non_fi = "Non-fiction"
    Novel = "Novel"


class BookStatuses(str, Enum):
    available = "available"
    Ordered = "Ordered"
    Exchanged = "Exchanged"



class UserBase(SQLModel):
    username: str
    email: str
    about_me: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}



class BookBase(BaseModel):
    title: str
    author: str
    genre: Genres
    published_year: int


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: int

    model_config = {"from_attributes": True}



class UserBookBase(SQLModel):
    user_id: int
    book_id: int
    status: BookStatuses


class UserBookCreate(UserBookBase):
    pass


class UserBookRead(UserBookBase):
    id: int
    user: Optional[UserRead] = None
    book: Optional[BookRead] = None

    model_config = {"from_attributes": True}



class OfferBase(SQLModel):
    sender_id: int
    receiver_id: int
    sender_book_id: int
    receiver_book_id: int
    sender_confirm: bool = False
    receiver_confirm: bool = False
    status: str = "pending"


class OfferCreate(OfferBase):
    pass


class OfferRead(OfferBase):
    id: int
    created_at: Optional[str] = None
    sender: Optional[UserRead] = None
    receiver: Optional[UserRead] = None
    sender_book: Optional[UserBookRead] = None
    receiver_book: Optional[UserBookRead] = None

    model_config = {"from_attributes": True}



class ExchangeBase(SQLModel):
    offer_id: int


class ExchangeCreate(ExchangeBase):
    pass


class ExchangeRead(ExchangeBase):
    id: int
    exchange_date: Optional[str] = None

    model_config = {"from_attributes": True}



class UserResponse(BaseModel):
    username: str
    model_config = {"from_attributes": True}


class BookSimpleResponse(BaseModel):
    title: str
    author: str
    model_config = {"from_attributes": True}


class UserBookResponse(BaseModel):
    id: int
    book: BookSimpleResponse
    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


class ExchangeResponse(BaseModel):
    id: int
    exchange_date: Optional[datetime] = None
    offer: OfferResponse
    model_config = {"from_attributes": True}
