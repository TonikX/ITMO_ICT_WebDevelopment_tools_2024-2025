from enum import Enum
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    bio: Optional[str] = None
    preferences: Optional[str] = None

    # связи
    books: List["Book"] = Relationship(back_populates="owner")
    sent_requests: List["ExchangeRequest"] = Relationship(back_populates="requester", sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requester_id"})
    received_requests: List["ExchangeRequest"] = Relationship(back_populates="owner", sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.owner_id"})


class BookTagLink(SQLModel, table=True):
    book_id: int = Field(foreign_key="book.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id",  primary_key=True)
    added_at: datetime | None

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    books: List["Book"] = Relationship(back_populates="tags", link_model=BookTagLink)


# книга, которую пользователь добавляет в библиотеку
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")

    owner: "User" = Relationship(back_populates="books")
    requests: List["ExchangeRequest"] = Relationship(back_populates="book")

    tags: List[Tag] = Relationship(back_populates="books", link_model=BookTagLink)


# статус запроса на обмен
class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# модель запроса на обмен
class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    requester_id: int = Field(foreign_key="user.id")
    owner_id: int = Field(foreign_key="user.id")
    status: RequestStatus = Field(default=RequestStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    book: Book = Relationship(back_populates="requests")
    requester: User = Relationship(back_populates="sent_requests", sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requester_id"})
    owner: User = Relationship(back_populates="received_requests", sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.owner_id"})


class TagRead(SQLModel):
    id: int
    name: str


class BookRead(SQLModel):
    id: int
    title: str
    description: Optional[str]
    tags: List[TagRead]
    owner: "UserRead"


class BookCreate(SQLModel):
    title: str
    description: Optional[str] = None
    owner_id: int


class ExchangeRequestRead(SQLModel):
    id: int
    status: RequestStatus
    book: BookRead
    requester: "UserRead"
    owner: "UserRead"


class UserShort(SQLModel):
    id: int
    username: str


class UserRead(SQLModel):
    id: int
    username: str
    books: List[BookRead]
    sent_requests: List[ExchangeRequestRead]
    received_requests: List[ExchangeRequestRead]


UserRead.model_rebuild()
BookRead.model_rebuild()
TagRead.model_rebuild()
ExchangeRequestRead.model_rebuild()
