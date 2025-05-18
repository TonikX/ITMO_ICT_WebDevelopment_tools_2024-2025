from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import SQLModel, Field, Relationship


class SwapStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    outdated = "outdated"

class Ownership(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    is_current: bool = Field(default=True)

    user: "User" = Relationship(back_populates="ownerships")
    book: "Book" = Relationship(back_populates="ownerships")

    offer: Optional["Offer"] = Relationship(
        back_populates="ownership",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}  # оффер удаляется, если удалено владение
    )

class User(SQLModel, table=True):
    """Модель пользователя."""
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    age: int | None = Field(default=None)
    info: str | None = Field(default=None)

    # один пользователь может иметь много владений
    ownerships: List[Ownership] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    books: List["Book"] = Relationship(
        back_populates="users",
        link_model=Ownership,
        sa_relationship_kwargs={"overlaps": "ownerships,user,book"}
    )

class BookGenre(SQLModel, table=True):
    """
    Связывающая таблица для установления отношения многие-ко-многим
    между книгами и жанрами. Используется составной первичный ключ.
    """
    book_id: int = Field(foreign_key="book.id", primary_key=True, index=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True, index=True)


class Book(SQLModel, table=True):
    """Модель книги."""
    id: int | None = Field(default=None, primary_key=True)
    name: str
    author: str
    year: int
    publisher: str

    # многие-ко-многим с жанрами через связывающую таблицу BookGenre
    genres: List["Genre"] = Relationship(
        back_populates="books",
        link_model=BookGenre
    )
    # один-ко-многим
    ownerships: List[Ownership] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    # многие-ко-многим
    users: List[User] = Relationship(
        back_populates="books",
        link_model=Ownership,
        sa_relationship_kwargs={"overlaps": "ownerships,book,user"}
    )


class Genre(SQLModel, table=True):
    """Модель жанра."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # обратная связь для связи многие-ко-многим с книгами
    books: List[Book] = Relationship(
        back_populates="genres",
        link_model=BookGenre
    )


class Offer(SQLModel, table=True):
    """Модель предложения на обмен."""
    id: int | None = Field(default=None, primary_key=True)
    ownership_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("ownership.id", ondelete="CASCADE"),
            unique=True,
            index=True
        )
    )
    is_open: bool = Field(default=True)
    comment: str | None = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    ownership: Ownership = Relationship(back_populates="offer")


class SwapRequest(SQLModel, table=True):
    """Модель запроса на обмен."""
    id: int | None = Field(default=None, primary_key=True)
    get_offer_id: int | None = Field(foreign_key="offer.id", index=True)
    give_offer_id: int = Field(foreign_key="offer.id", index=True)
    comment: str | None = Field(default="")
    status: SwapStatus = Field(default=SwapStatus.PENDING)

    # указание внешних ключей через sa_relationship_kwargs
    get_offer: Offer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SwapRequest.get_offer_id"}
    )
    give_offer: Offer = Relationship(
        sa_relationship_kwargs={"foreign_keys": "SwapRequest.give_offer_id"}
    )

class Deal(SQLModel, table=True):
    """Модель сделки обмена."""
    id: int | None = Field(default=None, primary_key=True)
    swap_id: int = Field(foreign_key="swaprequest.id", index=True)
    date_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    swap_request: SwapRequest = Relationship()


class BookParsed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    author: str
    year: int
    publisher: str
