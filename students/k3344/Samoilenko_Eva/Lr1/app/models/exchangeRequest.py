from typing import Optional
from sqlmodel import Field, Relationship
from ..schemas.exchangeRequest import ExchangeRequestBase
# from book import Book
# from profile import Profile
# from exchange import Exchange


class ExchangeRequest(ExchangeRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requester: "Profile" = Relationship()
    book: "Book" = Relationship()
    exchange: Optional["Exchange"] = Relationship(back_populates="exchange_request")
