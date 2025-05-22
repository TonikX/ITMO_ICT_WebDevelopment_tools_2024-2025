from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models import Event


class RegistrationSchema(BaseModel):
    user_id: int
    address: str
    skill: str
    name: str
    phone_number: str
    confirmed: bool


class SubmissionSchema(BaseModel):
    id: Optional[int]
    team_id: int

    dt_created: datetime
    score: Optional[int]

    attachment: str


class TeamBase(BaseModel):
    name: str
    description: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    event_id: int


class TeamInDB(TeamBase):
    id: int

    event: Event

    registrations: List["RegistrationSchema"]
    submissions: List["SubmissionSchema"]
