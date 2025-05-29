from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
from pydantic import validator, EmailStr


class ExchangeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class BookStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class BookItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    description: Optional[str] = None

    owners: List["UserBook"] = Relationship(back_populates="book_item")
    requested_in: List["ExchangeRequest"] = Relationship(
        back_populates="requested_book",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requested_book_id"}
    )
    offered_in: List["ExchangeRequest"] = Relationship(
        back_populates="offered_book",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.offered_book_id"}
    )


class BookExchange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exchange_request_id: int = Field(foreign_key="exchangerequest.id")
    user_profile_id: int = Field(foreign_key="userprofile.id")
    status: ExchangeStatus = Field(default=ExchangeStatus.PENDING)

    exchange_request: "ExchangeRequest" = Relationship(
        back_populates="exchange",
        sa_relationship_kwargs={"foreign_keys": "BookExchange.exchange_request_id"}
    )
    user_profile: "UserProfile" = Relationship(
        back_populates="exchanges",
        sa_relationship_kwargs={"foreign_keys": "BookExchange.user_profile_id"}
    )


class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="userprofile.id")
    requested_book_id: int = Field(foreign_key="bookitem.id")
    offered_book_id: Optional[int] = Field(foreign_key="bookitem.id", default=None)
    status: ExchangeStatus = Field(default=ExchangeStatus.PENDING)

    requester: "UserProfile" = Relationship(back_populates="exchange_requests_sent")
    requested_book: "BookItem" = Relationship(
        back_populates="requested_in",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requested_book_id"}
    )
    offered_book: Optional["BookItem"] = Relationship(
        back_populates="offered_in",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.offered_book_id"}
    )
    exchange: Optional["BookExchange"] = Relationship(back_populates="exchange_request")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password: str = Field(max_length=256, min_length=6)
    email: EmailStr

    profile: Optional["UserProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserProfile.user_id"}
    )


class UserInput(SQLModel):
    username: str
    password: str = Field(max_length=256, min_length=6)
    password2: str
    email: EmailStr

    @validator('password2')
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords don\'t match')
        return v


class UserLogin(SQLModel):
    username: str
    password: str


class UserBook(SQLModel, table=True):
    user_profile_id: int = Field(foreign_key="userprofile.id", primary_key=True)
    book_item_id: int = Field(foreign_key="bookitem.id", primary_key=True)
    status: BookStatus = Field(default=BookStatus.AVAILABLE)

    user_profile: "UserProfile" = Relationship(
        back_populates="books",
        sa_relationship_kwargs={"foreign_keys": "UserBook.user_profile_id"}
    )
    book_item: "BookItem" = Relationship(
        back_populates="owners",
        sa_relationship_kwargs={"foreign_keys": "UserBook.book_item_id"}
    )


class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="profile")
    exchange_requests_sent: List["ExchangeRequest"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requester_id"}
    )
    books: List["UserBook"] = Relationship(back_populates="user_profile")
    exchanges: List["BookExchange"] = Relationship(back_populates="user_profile")
