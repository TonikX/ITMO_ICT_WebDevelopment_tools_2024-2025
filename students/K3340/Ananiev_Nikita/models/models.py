from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from .default_models import ProfileDefault, BookDefault, BookInfoDefault, TagDefault, ShareRequestDefault

class BookTagLink(SQLModel, table=True):
    info_id: Optional[int] = Field(default=None, foreign_key='bookinfo.id', primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key='tag.id', primary_key=True)


class BookInfo(BookInfoDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    tags: Optional[list["Tag"]] = Relationship(back_populates="books", link_model=BookTagLink)
    instances: Optional[list["Book"]] = Relationship(back_populates="info")


class Book(BookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    owner_id: int = Field(default=None, foreign_key='profile.id')
    info_id: int = Field(default=None, foreign_key='bookinfo.id')

    info: Optional["BookInfo"] = Relationship(back_populates="instances")
    owner: Optional["Profile"] = Relationship(back_populates="books")


class Profile(ProfileDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    books: Optional[list[Book]] = Relationship(back_populates="owner")
    sent_requests: Optional[list["ShareRequest"]] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={
            "foreign_keys": "[ShareRequest.sender_id]"
        }
    )
    received_requests: Optional[list["ShareRequest"]] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={
            "foreign_keys": "[ShareRequest.receiver_id]"
        }
    )


class Tag(TagDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    books: Optional[list["BookInfo"]] = Relationship(back_populates="tags", link_model=BookTagLink)


class ShareRequest(ShareRequestDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    sender: Profile = Relationship(
        back_populates="sent_requests",
        sa_relationship_kwargs={
            "foreign_keys": "[ShareRequest.sender_id]"
        }
    )
    receiver: Profile = Relationship(
        back_populates="received_requests",
        sa_relationship_kwargs={
            "foreign_keys": "[ShareRequest.receiver_id]"
        }
    )
