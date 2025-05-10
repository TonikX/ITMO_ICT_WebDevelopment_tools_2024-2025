from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel

from model.schemas.organizer import OrganizerRead
from model.schemas.participant import ParticipantRead
from model.schemas.task import TaskRead
from model.schemas.user import UserReadShort


class HackathonBase(SQLModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime


class HackathonCreate(HackathonBase):
    organizer_id: int


class HackathonRead(HackathonBase):
    id: int
    organizer_id: int


class HackathonUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class HackathonReadDetailed(HackathonRead):
    main_organizer: Optional[UserReadShort]
    tasks: List[TaskRead] = []
    participants: List[ParticipantRead] = []
    organizers: List[OrganizerRead] = []