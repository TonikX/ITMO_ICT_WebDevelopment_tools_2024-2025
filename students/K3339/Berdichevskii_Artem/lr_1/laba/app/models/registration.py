from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint


class Skill(str, Enum):
    programmer = "programmer"
    analyst = "analyst"
    designer = "designer"


class Registration(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="unique_event_user"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    address: str
    phone_number: str
    skill: Skill
    confirmed: bool = Field(default=False)

    event_id: int = Field(foreign_key="event.id")
    event: Optional["Event"] = Relationship(back_populates="registrations", sa_relationship_kwargs={"lazy": "selectin"})

    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="registrations", sa_relationship_kwargs={"lazy": "selectin"})

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional["Team"] = Relationship(back_populates="registrations", sa_relationship_kwargs={"lazy": "selectin"})
