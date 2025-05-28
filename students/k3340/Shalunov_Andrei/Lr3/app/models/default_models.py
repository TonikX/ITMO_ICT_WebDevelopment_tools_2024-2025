from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field


class ProfileDefault(SQLModel):
    name: str
    password: str
    email: str = Field(unique=True, index=True)
    description: Optional[str] = None
    register_date: date
    birth_date: date


class BookInfoDefault(SQLModel):
    title: str
    author: str
    release_date: date
    publisher: Optional[str] = None
    genre: str


class BookDefault(SQLModel):
    owner_id: Optional[int] = Field(default=None, foreign_key="profile.id")
    info_id: Optional[int] = Field(default=None, foreign_key="bookinfo.id")
    print_date: Optional[date] = None
    own_since: date


class TagDefault(SQLModel):
    name: str


class ShareRequestDefault(SQLModel):
    sender_id:  Optional[int] = Field(default=None, foreign_key="profile.id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="profile.id")
    suggested_book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    received_book_id:  Optional[int] = Field(default=None, foreign_key="book.id")
    status: str
    requested_date: date