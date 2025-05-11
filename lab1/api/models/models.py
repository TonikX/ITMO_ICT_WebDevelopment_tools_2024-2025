from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class Status(str, Enum):
    available = "Доступна"
    exchanged = "Обменена"


class StatusExchange(str, Enum):
    pending = "Рассматривается"
    accepted = "Принято"
    declined = "Отклонено"
    completed = "Завершено"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    books: List["Book"] = Relationship(back_populates="user")

    sent_exchange_requests: List["ExchangeRequest"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"}
    )
    received_exchange_requests: List["ExchangeRequest"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"}
    )


class BookGenre(SQLModel, table=True):
    book_id: int = Field(foreign_key="book.id", primary_key=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True)

    book: Optional["Book"] = Relationship(back_populates="book_genres")


class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    books: List["Book"] = Relationship(back_populates="genres", link_model=BookGenre)


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    author: str
    description: str
    status: Status = Field(default=Status.available)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="books")

    book_genres: List[BookGenre] = Relationship(back_populates="book")

    genres: List[Genre] = Relationship(back_populates="books", link_model=BookGenre)

    sent_exchange_requests: List["ExchangeRequest"] = Relationship(
        back_populates="sender_book",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"}
    )

    received_exchange_requests: List["ExchangeRequest"] = Relationship(
        back_populates="requested_book",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.requested_book_id]"}
    )


class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")

    sender_book_id: int = Field(foreign_key="book.id")
    requested_book_id: int = Field(foreign_key="book.id")

    status: StatusExchange = Field(default=StatusExchange.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sender: Optional["User"] = Relationship(
        back_populates="sent_exchange_requests",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"}
    )
    receiver: Optional["User"] = Relationship(
        back_populates="received_exchange_requests",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"}
    )

    sender_book: Optional["Book"] = Relationship(
        back_populates="sent_exchange_requests",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"}
    )
    requested_book: Optional["Book"] = Relationship(
        back_populates="received_exchange_requests",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.requested_book_id]"}
    )
