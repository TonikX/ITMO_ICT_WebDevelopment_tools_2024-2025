from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="profile")
    exchange_requests_sent: List["ExchangeRequest"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.requester_id"}
    )
    books: List["UserBook"] = Relationship(back_populates="user_profile")
    exchanges: List["BookExchange"] = Relationship(back_populates="user_profile")
