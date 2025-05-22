import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str

    dt_end_registration: datetime.date
    dt_event_start: datetime.date
    dt_event_end: datetime.date

    tasks: Optional[List["Task"]] = Relationship(back_populates="event", sa_relationship_kwargs={'lazy': 'selectin'})
    registrations: Optional[List["Registration"]] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    teams: Optional[List["Team"]] = Relationship(back_populates="event", sa_relationship_kwargs={'lazy': 'selectin'})
