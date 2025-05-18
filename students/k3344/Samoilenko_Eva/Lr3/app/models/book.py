from typing import Optional, List
from sqlmodel import Field, Relationship

from ..schemas.book import BookBase
from ..models.exchangeRequest import ExchangeRequest


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_library_id: int = Field(foreign_key="profilelibrary.id")
    requests: List[ExchangeRequest] = Relationship(back_populates="book")
