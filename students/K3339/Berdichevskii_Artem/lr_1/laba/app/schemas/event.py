import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models import Task, Registration


class EventBase(BaseModel):
    title: str
    description: str

    dt_end_registration: datetime.date
    dt_event_start: datetime.date
    dt_event_end: datetime.date


class EventList(EventBase):
    id: int


class EventInDb(EventList):
    tasks: Optional[List["Task"]]
    registrations: Optional[List["Registration"]]
