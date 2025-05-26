from enum import Enum

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class UserDefault(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    bio: Optional[str] = None


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserRead(UserDefault):
    id: int


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    bio: Optional[str] = None


class UserLogin(SQLModel):
    username: str
    password: str


class User(UserDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    library: List["Library"] = Relationship(back_populates="user")
    sent_requests: List["ExchangeRequest"] = Relationship(back_populates="requester", sa_relationship_kwargs={
        "foreign_keys": "[ExchangeRequest.requester_id]"})
    received_requests: List["ExchangeRequest"] = Relationship(back_populates="owner", sa_relationship_kwargs={
        "foreign_keys": "[ExchangeRequest.owner_id]"})


class GenreDefault(SQLModel):
    name: str


class GenreRead(GenreDefault):
    id: int


class GenreCreate(GenreDefault):
    pass


class GenreUpdate(SQLModel):
    name: Optional[str] = None


class Genre(GenreDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    books: List["BookGenre"] = Relationship(back_populates="genre")


class BookGenre(SQLModel, table=True):
    book_id: int = Field(foreign_key="book.id", primary_key=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True)
    book: "Book" = Relationship()
    genre: Genre = Relationship()


class BookDefault(SQLModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None


class BookCreate(BookDefault):
    pass


class BookRead(BookDefault):
    id: int
    genres: List["Genre"]


class BookUpdate(BookDefault):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None


class Book(BookDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    libraries: List["Library"] = Relationship(back_populates="book")
    genres: List["Genre"] = Relationship(link_model=BookGenre)


class LibraryUpdate(SQLModel):
    is_available: bool


class UserBookRead(SQLModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    isbn: Optional[str] = None
    is_available: bool


class Library(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    book_id: int = Field(foreign_key="book.id", primary_key=True)
    is_available: bool = Field(default=True)
    user: User = Relationship(back_populates="library")
    book: Book = Relationship(back_populates="libraries")


class StatusExchangeRequest(Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class ExchangeRequestDefault(SQLModel):
    requester_id: int = Field(foreign_key="user.id")
    owner_id: int = Field(foreign_key="user.id")
    requested_book_id: int = Field(foreign_key="book.id")
    offered_book_id: int = Field(foreign_key="book.id")
    status: StatusExchangeRequest = Field(default=StatusExchangeRequest.pending)
    created_at: datetime = Field(default_factory=datetime.now)


class ExchangeRequestCreate(SQLModel):
    requested_book_id: int
    offered_book_id: int
    owner_id: int


class ExchangeResponse(SQLModel):
    decision: StatusExchangeRequest


class ExchangeRequest(ExchangeRequestDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requester: User = Relationship(back_populates="sent_requests",
                                   sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.requester_id]"})
    owner: User = Relationship(back_populates="received_requests",
                               sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.owner_id]"})
    requested_book: Book = Relationship(sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.requested_book_id]"})
    offered_book: Book = Relationship(sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.offered_book_id]"})


class ExchangeRequestRead(SQLModel):
    id: int
    status: StatusExchangeRequest
    created_at: datetime
    requester: UserRead
    owner: UserRead
    requested_book: BookRead
    offered_book: BookRead
