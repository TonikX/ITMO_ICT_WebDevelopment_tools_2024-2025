from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ScheduleRead(BaseModel):
    id: int
    productivity_score: int
    notes: str

    class Config:
        orm_mode = True