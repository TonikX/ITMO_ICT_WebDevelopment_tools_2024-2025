from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str
    bio: str
    date_joined: datetime = Field(default_factory=datetime.utcnow)
    library: Optional[List["Library"]] = Relationship(back_populates="user")


class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: str
    published_in: Optional[int]
    isbn: Optional[str]
    description: Optional[str]
    publisher: str
    libraries: Optional[List["Library"]] = Relationship(back_populates="book")


class Library(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    book_status: str

    user: User = Relationship(back_populates="library")
    book: Book = Relationship(back_populates="libraries")


class ExchangeStatus(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    exchange_requests: List["ExchangeRequest"] = Relationship(back_populates="status")


class ExchangeRequest(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    from_user_id: int = Field(foreign_key="user.id")
    to_user_id: int = Field(foreign_key="user.id")
    library_id: int = Field(foreign_key="library.id")
    status_id: int = Field(foreign_key="exchangestatus.id")

    request_date: Optional[datetime] = None
    exchange_date: Optional[datetime] = None
    status: ExchangeStatus = Relationship(back_populates="exchange_requests")
