from enum import Enum
from typing import Optional, List
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, Relationship

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Genres(str, Enum):
    sci_fi = "Science Fiction"
    non_fi = "Non-fiction"
    novel = "Novel"


class BookStatuses(str, Enum):
    available = "available"
    ordered = "Ordered"
    exchanged = "Exchanged"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    about_me: Optional[str] = None
    created_at: Optional[str] = None

    books: List["UserBook"] = Relationship(back_populates="user")
    sent_offers: List["Offer"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Offer.sender_id"}
    )
    received_offers: List["Offer"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "Offer.receiver_id"}
    )

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)


class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: Genres
    published_year: int

    user_books: List["UserBook"] = Relationship(back_populates="book")


class UserBook(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    status: BookStatuses

    user: Optional[User] = Relationship(back_populates="books")
    book: Optional[Book] = Relationship(back_populates="user_books")

    sent_offers: List["Offer"] = Relationship(
        back_populates="sender_book",
        sa_relationship_kwargs={"foreign_keys": "Offer.sender_book_id"}
    )
    received_offers: List["Offer"] = Relationship(
        back_populates="receiver_book",
        sa_relationship_kwargs={"foreign_keys": "Offer.receiver_book_id"}
    )


class Offer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    sender_id: Optional[int] = Field(default=None, foreign_key="user.id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="user.id")
    sender_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    receiver_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    sender_confirm: bool = False
    receiver_confirm: bool = False
    status: str = "pending"
    created_at: Optional[str] = None

    sender: Optional[User] = Relationship(
        back_populates="sent_offers",
        sa_relationship_kwargs={"foreign_keys": "Offer.sender_id"}
    )
    receiver: Optional[User] = Relationship(
        back_populates="received_offers",
        sa_relationship_kwargs={"foreign_keys": "Offer.receiver_id"}
    )
    sender_book: Optional[UserBook] = Relationship(
        back_populates="sent_offers",
        sa_relationship_kwargs={"foreign_keys": "Offer.sender_book_id"}
    )
    receiver_book: Optional[UserBook] = Relationship(
        back_populates="received_offers",
        sa_relationship_kwargs={"foreign_keys": "Offer.receiver_book_id"}
    )
    exchange: Optional["Exchange"] = Relationship(back_populates="offer")


class Exchange(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id")
    exchange_date: Optional[str] = None

    offer: Optional[Offer] = Relationship(back_populates="exchange")
