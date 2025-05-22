from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str

    event_id: int = Field(foreign_key="event.id")

    event: Optional["Event"] = Relationship(back_populates="teams", sa_relationship_kwargs={'lazy': 'selectin'})
    registrations: List["Registration"] = Relationship(back_populates="team", sa_relationship_kwargs={'lazy': 'selectin'})
    submissions: List["Submission"] = Relationship(back_populates="team", sa_relationship_kwargs={'lazy': 'selectin'})
