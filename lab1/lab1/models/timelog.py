from sqlmodel import SQLModel
from typing import Optional


class TimeLogCreate(SQLModel):
    task_id: int
    start_time: str
    end_time: Optional[str] = None


class TimeLogRead(SQLModel):
    id: int
    task_id: int
    start_time: str
    end_time: Optional[str] = None
