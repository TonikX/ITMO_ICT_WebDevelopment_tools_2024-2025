from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from .enums import ExchangeStatus


class BookExchange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exchange_request_id: int = Field(foreign_key="exchangerequest.id")
    user_profile_id: int = Field(foreign_key="userprofile.id")
    status: ExchangeStatus = Field(default=ExchangeStatus.PENDING)

    exchange_request: "ExchangeRequest" = Relationship(
        back_populates="exchange",
        sa_relationship_kwargs={"foreign_keys": "BookExchange.exchange_request_id"}
    )
    user_profile: "UserProfile" = Relationship(
        back_populates="exchanges",
        sa_relationship_kwargs={"foreign_keys": "BookExchange.user_profile_id"}
    )
