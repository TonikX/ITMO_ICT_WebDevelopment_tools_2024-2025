from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class BookStatus(str, Enum):
    available = "available"
    exchanged = "exchanged"


class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    full_name: str
    bio: Optional[str] = None
    skills: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    preferences: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    books: List["Book"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete"})
    libraries: List["Library"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    sent_requests: List["ExchangeRequest"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"}
    )

    received_requests: List["ExchangeRequest"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"}
    )
    sent_exchanges: List["Exchange"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.sender_id]", "cascade": "all, delete-orphan"}
    )

    received_exchanges: List["Exchange"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.receiver_id]", "cascade": "all, delete-orphan"}
    )


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: str
    description: str
    status: BookStatus
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="books")
    exchange_requests: List["ExchangeRequest"] = Relationship(back_populates="book",
                                                              sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    exchanges: List["Exchange"] = Relationship(back_populates="book",
                                               sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Exchange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    book: Optional["Book"] = Relationship(back_populates="exchanges", sa_relationship_kwargs={"lazy": "selectin"})
    sender: Optional[User] = Relationship(
        back_populates="sent_exchanges",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.sender_id]"}
    )
    receiver: Optional[User] = Relationship(
        back_populates="received_exchanges",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.receiver_id]"}
    )


class Library(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="libraries")
    books: List["LibraryBook"] = Relationship(back_populates="library", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    message: Optional[str] = None
    status: RequestStatus = RequestStatus.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sender: User = Relationship(back_populates="sent_requests",
                                sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"})
    receiver: User = Relationship(back_populates="received_requests",
                                  sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"})
    book: Optional["Book"] = Relationship(back_populates="exchange_requests", sa_relationship_kwargs={"lazy": "selectin"})


class LibraryBook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    library_id: int = Field(foreign_key="library.id")
    book_id: int = Field(foreign_key="book.id")
    library: Optional["Library"] = Relationship(back_populates="books")
    book: Optional["Book"] = Relationship()


class UserDefault(SQLModel):
    username: str
    email: str
    password: str
    full_name: str
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    preferences: Optional[List[str]] = None


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    preferences: Optional[List[str]] = None


class LoginRequest(SQLModel):
    email: str
    password: str


class PasswordChangeRequest(SQLModel):
    old_password: str
    new_password: str


class ExchangeUpdate(SQLModel):
    book_id: Optional[datetime] = None
    sender_id: Optional[datetime] = None
    receiver_id: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UserPublic(SQLModel):
    id: int
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    preferences: Optional[List[str]] = None


class BookInfo(SQLModel):
    id: int
    title: str
    author: str
    genre: str
    description: str
    status: BookStatus
    owner: Optional[UserPublic]


class ExchangeInfo(SQLModel):
    id: int
    sender: UserPublic
    receiver: UserPublic
    book: BookInfo
    start_date: datetime
    end_date: Optional[datetime] = None


class BookCreate(SQLModel):
    title: str
    author: str
    genre: str
    description: str
    status: BookStatus


class ExchangeCreate(SQLModel):
    request_id: int
    book_id: int
    sender_id: int
    receiver_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class LibraryCreate(SQLModel):
    name: Optional[str] = None
    user_id: int
    book_ids: List[int]


class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BookStatus] = None


class ExchangeRequestCreate(SQLModel):
    sender_id: int
    receiver_id: int
    book_id: int
    message: Optional[str] = None


class ExchangeRequestUpdate(SQLModel):
    status: Optional[RequestStatus] = None


class ExchangeRequestInfo(SQLModel):
    id: int
    sender: UserPublic
    receiver: UserPublic
    book: BookInfo
    message: Optional[str] = None
    status: RequestStatus
    created_at: datetime


class LibraryUpdate(SQLModel):
    user_id: Optional[int] = None
    books: Optional[List[int]] = None


class LibraryBookInfo(SQLModel):
    book: BookInfo


class LibraryInfo(SQLModel):
    id: int
    name: Optional[str]
    user: Optional[UserPublic]
    books: List[LibraryBookInfo]
