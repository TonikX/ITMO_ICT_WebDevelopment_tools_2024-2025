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
    library: Optional[List["Library"]] = Relationship(back_populates="user")  # Связь с библиотекой


class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: str
    published_in: Optional[int]
    isbn: Optional[str]
    description: Optional[str]
    publisher: str
    libraries: Optional[List["Library"]] = Relationship(back_populates="book")  # Связь с библиотекой


class BookCreate(SQLModel):
    title: str
    author: str
    genre: str
    published_in: Optional[int]
    isbn: Optional[str]
    description: Optional[str]
    publisher: str


class Library(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # Связь с пользователем
    book_id: int = Field(foreign_key="book.id")  # Связь с книгой
    book_status: str  # Например, "Доступна", "Не доступна", "В процессе обмена"

    user: User = Relationship(back_populates="library")  # Обратная связь
    book: Book = Relationship(back_populates="libraries")  # Обратная связь


class ExchangeStatus(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    exchange_requests: List["ExchangeRequest"] = Relationship(back_populates="status")


class ExchangeRequest(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    from_user_id: int = Field(foreign_key="user.id")
    to_user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")

    status_id: int = Field(foreign_key="exchangestatus.id")

    request_date: Optional[datetime] = None
    exchange_date: Optional[datetime] = None
    status: ExchangeStatus = Relationship(back_populates="exchange_requests")


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    bio: str


class UserCreate(SQLModel):
    username: str
    email: str
    password_hash: str
    bio: str
    date_joined: datetime = Field(default_factory=datetime.utcnow)


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

