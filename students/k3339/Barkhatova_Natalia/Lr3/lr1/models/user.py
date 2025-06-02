from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    password: str
    username: str
    preferences: Optional[str] = None

    books_as_owner: List["Book"] = Relationship(back_populates="owner",
                                                sa_relationship_kwargs={"foreign_keys": "[Book.owner_id]"})
    books_as_previous_owner: List["Book"] = Relationship(back_populates="previous_owner", sa_relationship_kwargs={
        "foreign_keys": "[Book.previous_owner_id]"})

    reviews_written: List["Review"] = Relationship(back_populates="author",
                                                   sa_relationship_kwargs={"foreign_keys": "[Review.user_id]"})
    reviews_received: List["Review"] = Relationship(back_populates="target", sa_relationship_kwargs={
        "foreign_keys": "[Review.reviewed_user_id]"})
    location: Optional["Location"] = Relationship(back_populates="user")
    exchanges_as_owner: List["Exchange"] = Relationship(back_populates="owner",
                                                        sa_relationship_kwargs={"foreign_keys": "[Exchange.owner_id]"})
    exchanges_as_requester: List["Exchange"] = Relationship(back_populates="requester", sa_relationship_kwargs={
        "foreign_keys": "[Exchange.requester_id]"})
