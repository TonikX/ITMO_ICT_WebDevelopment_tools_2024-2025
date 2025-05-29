from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from .default_models import (
    ProfileDefault,
    BookDefault,
    BookInfoDefault,
    TagDefault,
    ShareRequestDefault,
)


class BookTagLink(SQLModel, table=True):
    info_id: Optional[int] = Field(
        default=None, foreign_key="bookinfo.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
    added_at: datetime = Field(default_factory=datetime.utcnow)


class BookInfo(BookInfoDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tags: List["Tag"] = Relationship(
        back_populates="books",
        link_model=BookTagLink,
    )
    instances: List["Book"] = Relationship(back_populates="info")


class Book(BookDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    info: Optional[BookInfo] = Relationship(back_populates="instances")
    owner: Optional["Profile"] = Relationship(back_populates="books")


class Profile(ProfileDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    books: List[Book] = Relationship(back_populates="owner")
    sent_requests: List["ShareRequest"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[ShareRequest.sender_id]"},
    )
    received_requests: List["ShareRequest"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "[ShareRequest.receiver_id]"},
    )


class Tag(TagDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    books: List[BookInfo] = Relationship(
        back_populates="tags",
        link_model=BookTagLink,
    )



class ShareRequest(ShareRequestDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    sender: Profile = Relationship(
        back_populates="sent_requests",
        sa_relationship_kwargs={"foreign_keys": "[ShareRequest.sender_id]"},
    )
    receiver: Profile = Relationship(
        back_populates="received_requests",
        sa_relationship_kwargs={"foreign_keys": "[ShareRequest.receiver_id]"},
    )
    suggested_book: Optional[Book] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ShareRequest.suggested_book_id]"},
    )
    received_book: Optional[Book] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ShareRequest.received_book_id]"},
    )