from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from enums.book_status import BookStatus
from enums.genre import BookGenre


class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    title: str
    author: str
    genre: BookGenre
    book_status: Optional[BookStatus] = Field(default=BookStatus.available)
    owner_comment: Optional[str] = None
    previous_owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    owner: "User" = Relationship(back_populates="books_as_owner",
                                 sa_relationship_kwargs={"foreign_keys": "[Book.owner_id]"})
    previous_owner: Optional["User"] = Relationship(back_populates="books_as_previous_owner",
                                                    sa_relationship_kwargs={"foreign_keys": "[Book.previous_owner_id]"})
    owner_exchanges: List["Exchange"] = Relationship(back_populates="owner_book", sa_relationship_kwargs={
        "foreign_keys": "[Exchange.owner_book_id]"})
    requester_exchanges: List["Exchange"] = Relationship(back_populates="requester_book", sa_relationship_kwargs={
        "foreign_keys": "[Exchange.requester_book_id]"})
