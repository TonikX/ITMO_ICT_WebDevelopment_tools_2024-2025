from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Hackathon(SQLModel, table=True):
    __tablename__ = "hackathons"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_name: str = Field(nullable=False)
    description: Optional[str] = None
    start_date: datetime = Field(nullable=False)
    end_date: datetime = Field(nullable=False)

    tasks: List["Task"] = Relationship(
        back_populates="hackathon",
        sa_relationship_kwargs={"primaryjoin": "Hackathon.id == Task.hackathon_id"}
    )

# Схемы для API

class HackathonCreate(SQLModel):
    event_name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime

class HackathonRead(SQLModel):
    id: int
    event_name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime