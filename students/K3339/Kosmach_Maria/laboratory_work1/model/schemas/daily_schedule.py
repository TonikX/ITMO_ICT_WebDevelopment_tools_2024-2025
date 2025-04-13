from datetime import datetime

from pydantic import BaseModel

class DailyScheduleCreate(BaseModel):
    user_id: int
    date: datetime


class DailyScheduleRead(DailyScheduleCreate):
    id: int

class DailyScheduleReadShort(BaseModel):
    id: int
    date: datetime