from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


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

