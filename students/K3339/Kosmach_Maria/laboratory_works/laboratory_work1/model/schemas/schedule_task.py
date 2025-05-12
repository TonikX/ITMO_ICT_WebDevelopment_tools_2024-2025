from datetime import time
from typing import Optional

from pydantic import BaseModel


class ScheduleTaskCreate(BaseModel):
    schedule_id: int
    task_id: int
    planned_time: Optional[time] = None


class ScheduleTaskRead(ScheduleTaskCreate):
    pass