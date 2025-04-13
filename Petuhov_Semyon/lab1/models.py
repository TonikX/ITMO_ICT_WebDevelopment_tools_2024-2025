from enum import Enum
from typing import Optional, List
from passlib.context import CryptContext

#from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Genres(Enum):
    sci_fi = "Science Fiction"
    non_fi = "Non-fiction"
    Novel = "Novel"

class BookStatuses(Enum):
    available = "available"
    Ordered = "Ordered"
    Exchanged = "Exchanged"

class UserDefault(SQLModel):
    username: str
    email: str
    about_me: Optional[str] = None

class User(UserDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: Optional[str] = None
    books: List["UserBook"] = Relationship(back_populates="user")
    sent_offers: List["Offer"] = Relationship(back_populates="sender", sa_relationship_kwargs={"foreign_keys": "Offer.sender_id"})
    received_offers: List["Offer"] = Relationship(back_populates="receiver", sa_relationship_kwargs={"foreign_keys": "Offer.receiver_id"})

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

class BookDefault(SQLModel):
    title: str
    author: str
    genre: Genres
    published_year: int

class Book(BookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user_books: List["UserBook"] = Relationship(back_populates="book")

class UserBookDefault(SQLModel):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")
    status: BookStatuses

class UserBook(UserBookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
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




class OfferDefault(SQLModel):
    sender_id: Optional[int] = Field(default=None, foreign_key="user.id")
    receiver_id: Optional[int] = Field(default=None, foreign_key="user.id")
    sender_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    receiver_book_id: Optional[int] = Field(default=None, foreign_key="userbook.id")
    sender_confirm: bool = False
    receiver_confirm: bool = False
    status: str = "pending"

class Offer(OfferDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: Optional[str] = None
    sender: Optional[User] = Relationship(back_populates="sent_offers",
                                          sa_relationship_kwargs={"foreign_keys": "Offer.sender_id"}
                                          )
    receiver: Optional[User] = Relationship(back_populates="received_offers",
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

class ExchangeDefault(SQLModel):
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id")

class Exchange(ExchangeDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id")
    exchange_date: Optional[str] = None
    offer: Optional[Offer] = Relationship(back_populates="exchange")


