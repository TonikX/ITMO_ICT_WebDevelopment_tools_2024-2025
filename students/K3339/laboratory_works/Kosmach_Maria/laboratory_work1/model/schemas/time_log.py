from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimeLogCreate(BaseModel):
    task_id: int
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None


class TimeLogRead(TimeLogCreate):
    id: int