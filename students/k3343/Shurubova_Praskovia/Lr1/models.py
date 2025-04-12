from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from datetime import datetime


class BookStatus(str, Enum):
    available = "available"
    exchanged = "exchanged"


class ExchangeRole(str, Enum):
    sender = "sender"
    receiver = "receiver"


class Library(SQLModel, table=True):
    library_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    user: Optional["User"] = Relationship(back_populates="library", sa_relationship_kwargs={"cascade": "all, delete"})
    book: Optional["Book"] = Relationship(back_populates="libraries", sa_relationship_kwargs={"cascade": "all, delete"})


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
    library: List["Library"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"})


class LoginRequest(SQLModel):
    email: str
    password: str


class PasswordChangeRequest(SQLModel):
    old_password: str
    new_password: str


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: str
    description: str
    status: BookStatus
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="books", sa_relationship_kwargs={"cascade": "all, delete"})
    libraries: List["Library"] = Relationship(back_populates="book", sa_relationship_kwargs={"cascade": "all, delete"})



class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Exchange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="exchangerequest.id")
    book_id: int = Field(foreign_key="book.id")
    role: ExchangeRole


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


class BookCreate(SQLModel):
    title: str
    author: str
    genre: str
    description: str
    status: BookStatus


class ExchangeCreate(SQLModel):
    request_id: int
    book_id: int
    role: ExchangeRole


class ExchangeRequestCreate(SQLModel):
    sender_id: int
    receiver_id: int
    status: str


class LibraryCreate(SQLModel):
    user_id: int
    book_id: int


class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BookStatus] = None


class ExchangeUpdate(SQLModel):
    book_id: Optional[int] = None
    role: Optional[str] = None


class ExchangeRequestUpdate(SQLModel):
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    status: Optional[str] = None


class LibraryUpdate(SQLModel):
    user_id: Optional[int] = None
    book_id: Optional[int] = None