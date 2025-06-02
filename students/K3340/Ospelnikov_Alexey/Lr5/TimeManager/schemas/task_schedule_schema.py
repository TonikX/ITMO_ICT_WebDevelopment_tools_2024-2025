from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class TaskScheduleCreate(BaseModel):
    urgency: str
    id: int

class TaskScheduleRead(BaseModel):
    id: int
    urgency: int
    schedule_id: bool
    task_id: int
    class Config:
        orm_mode = True