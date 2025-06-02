from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class NotificationCreate(BaseModel):
    message: str
    is_read: bool = False

class NotificationRead(BaseModel):
    id: int
    message: str
    is_read: bool
    task_id: int
    class Config:
        orm_mode = True