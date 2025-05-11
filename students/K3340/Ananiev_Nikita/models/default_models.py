from datetime import date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel


class ProfileDefault(SQLModel):
    name: str
    password: str
    email: str = Field(unique=True)
    description: str
    register_date: date
    birth_date: date


class AuthModel(BaseModel):
    email: str
    password: str


class BookDefault(SQLModel):
    owner_id: int = Field(default=None, foreign_key='profile.id')
    info_id: int = Field(default=None, foreign_key='bookinfo.id')
    print_date: date | None = None
    own_since: date


class BookInfoDefault(SQLModel):
    title: str
    author: str
    release_date: date
    publisher: str | None = None
    genre: str


class TagDefault(SQLModel):
    name: str


class ShareRequestDefault(SQLModel):
    sender_id: Optional[int] = Field(default=None, foreign_key='profile.id')
    receiver_id: Optional[int] = Field(default=None, foreign_key='profile.id')
    suggested_book_id: Optional[int] = Field(default=None, foreign_key='book.id')
    received_book_id: Optional[int] = Field(default=None, foreign_key='book.id')
    status: str
    requested_date: date
