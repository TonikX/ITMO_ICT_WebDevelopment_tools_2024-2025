from .models import *
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel


class BookCreate(SQLModel):
    title: str
    author: str
    genre: str
    published_in: Optional[int]
    isbn: Optional[str]
    description: Optional[str]
    publisher: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    bio: str
    date_joined: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    bio: str
    date_joined: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(BaseModel):
    status: int
    data: UserRead


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


class BookRead(SQLModel):
    id: int
    title: str
    author: str


class LibraryBase(SQLModel):
    book_status: str
    user_id: int
    book_id: int


class LibraryRead(LibraryBase):
    id: int
    user: UserRead
    book: BookRead


class ExchangeRequestBase(SQLModel):
    from_user_id: int
    to_user_id: int
    book_id: int
    status_id: int


class ExchangeRequestRead(ExchangeRequestBase):
    id: int
    request_date: Optional[datetime]
    exchange_date: Optional[datetime]
    status: ExchangeStatus


class Token(BaseModel):
    access_token: str
    token_type: str
