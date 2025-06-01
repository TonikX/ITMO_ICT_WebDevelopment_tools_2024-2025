from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

from enums.change_status import ChangeStatus


class Exchange(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)
    requester_id: int = Field(foreign_key="user.id", index=True)
    owner_book_id: int = Field(foreign_key="book.id", index=True)
    requester_book_id: int = Field(foreign_key="book.id", index=True)
    change_status: ChangeStatus
    created_at: datetime = Field(default=datetime.utcnow)

    owner: "User" = Relationship(back_populates="exchanges_as_owner",
                                 sa_relationship_kwargs={"foreign_keys": "[Exchange.owner_id]", "lazy": "select"})
    requester: "User" = Relationship(back_populates="exchanges_as_requester",
                                     sa_relationship_kwargs={"foreign_keys": "[Exchange.requester_id]",
                                                             "lazy": "select"})
    owner_book: "Book" = Relationship(back_populates="owner_exchanges",
                                      sa_relationship_kwargs={"foreign_keys": "[Exchange.owner_book_id]",
                                                              "lazy": "select"})
    requester_book: "Book" = Relationship(back_populates="requester_exchanges",
                                          sa_relationship_kwargs={"foreign_keys": "[Exchange.requester_book_id]",
                                                                  "lazy": "select"})
