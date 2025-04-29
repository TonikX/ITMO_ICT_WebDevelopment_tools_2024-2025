from typing import Optional
from sqlmodel import Field, Relationship
from ..schemas.exchange import ExchangeBase
# from profile import Profile
# from exchangeRequest import ExchangeRequest


class Exchange(ExchangeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="profile.id")
    owner_id: int = Field(foreign_key="profile.id")
    book_id: int = Field(foreign_key="book.id")
    exchange_request: "ExchangeRequest" = Relationship(back_populates="exchange")
    owner: "Profile" = Relationship(sa_relationship_kwargs={"primaryjoin": "Exchange.owner_id == "
                                                                           "Profile.id"})
