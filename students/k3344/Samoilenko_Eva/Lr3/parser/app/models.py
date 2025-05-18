from sqlmodel import SQLModel, Field, Relationship
import datetime
from typing import Optional, List

from pydantic import EmailStr


class BookBase(SQLModel):
    title: str
    author: str
    description: Optional[str] = None


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_library_id: int = Field(foreign_key="profilelibrary.id")
    requests: List["ExchangeRequest"] = Relationship(back_populates="book")


class ExchangeRequestBase(SQLModel):
    status: str = Field(default="pending")
    requester_id: int = Field(foreign_key="profile.id")
    requested_book_id: int = Field(foreign_key="book.id")


class ExchangeRequest(ExchangeRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requester: "Profile" = Relationship()
    book: "Book" = Relationship()
    exchange: Optional["Exchange"] = Relationship(back_populates="exchange_request")


class ExchangeBase(SQLModel):
    exchange_request_id: int = Field(foreign_key="exchangerequest.id")
    completed: bool = Field(default=True)


class Exchange(ExchangeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="profile.id")
    owner_id: int = Field(foreign_key="profile.id")
    book_id: int = Field(foreign_key="book.id")
    exchange_request: "ExchangeRequest" = Relationship(back_populates="exchange")
    owner: "Profile" = Relationship(sa_relationship_kwargs={"primaryjoin": "Exchange.owner_id == "
                                                                           "Profile.id"})


class ProfileBase(SQLModel):
    username: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None


class Profile(ProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    library: Optional["ProfileLibrary"] = Relationship(back_populates="owner")

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="profile")


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    username: str = Field(index=True)
    password: str = Field(max_length=256, min_length=6)
    email: EmailStr
    created_at: datetime.datetime = datetime.datetime.now()

    profile: Optional["Profile"] = Relationship(back_populates="user")


class ProfileLibraryBase(SQLModel):
    profile_id: int = Field(foreign_key="profile.id")


class ProfileLibrary(ProfileLibraryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner: "Profile" = Relationship(back_populates="library")
    books: List[Book] = Relationship()


class BookParsed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author: str
    title: str
    description: Optional[str]
