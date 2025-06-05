from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

from .enums import ExchangeStatus


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
