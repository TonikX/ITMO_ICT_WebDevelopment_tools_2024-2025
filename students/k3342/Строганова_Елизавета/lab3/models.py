from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


# ---------- USER ----------
class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    profile_info: Optional[str] = None
    skills: Optional[str] = None
    preferences: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    books: List["UserBook"] = Relationship(back_populates="user")
    sent_requests: List["ExchangeRequest"] = Relationship(back_populates="sender", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"})
    received_requests: List["ExchangeRequest"] = Relationship(back_populates="receiver", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"})


# ---------- BOOK ----------
class Book(SQLModel, table=True):
    book_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    publication_year: int
    condition: str
    description: Optional[str] = None

    owners: List["UserBook"] = Relationship(back_populates="book")


# ---------- USERBOOK ----------
class UserBook(SQLModel, table=True):
    user_book_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    book_id: int = Field(foreign_key="book.book_id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    status: str  # доступна / недоступна
    location: Optional[str] = None

    user: "User" = Relationship(back_populates="books")
    book: "Book" = Relationship(back_populates="owners")

    sender_requests: List["ExchangeRequest"] = Relationship(back_populates="sender_book", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"})
    receiver_requests: List["ExchangeRequest"] = Relationship(back_populates="desired_book", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.desired_book_id]"})


# ---------- EXCHANGEREQUEST ----------
class ExchangeRequest(SQLModel, table=True):
    request_id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.user_id")
    receiver_id: int = Field(foreign_key="user.user_id")
    sender_book_id: int = Field(foreign_key="userbook.user_book_id")
    desired_book_id: int = Field(foreign_key="userbook.user_book_id")
    status: str  # pending / accepted / rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None

    sender: "User" = Relationship(back_populates="sent_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"})
    receiver: "User" = Relationship(back_populates="received_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"})
    sender_book: "UserBook" = Relationship(back_populates="sender_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"})
    desired_book: "UserBook" = Relationship(back_populates="receiver_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.desired_book_id]"})
    exchange: Optional["Exchange"] = Relationship(back_populates="request")


# ---------- EXCHANGE ----------
class Exchange(SQLModel, table=True):
    exchange_id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="exchangerequest.request_id", unique=True)
    exchange_date: datetime = Field(default_factory=datetime.utcnow)
    completion_status: str  # в процессе / завершен
    user1_rating: Optional[int] = None
    user2_rating: Optional[int] = None
    feedback: Optional[str] = None

    request: "ExchangeRequest" = Relationship(back_populates="exchange")