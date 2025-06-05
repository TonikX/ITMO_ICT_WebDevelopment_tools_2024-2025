from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TaskBase(BaseModel):
    description: str
    due_date: datetime
    priority: str

    class Config:
        orm_mode = True


class TaskCreate(TaskBase):
    pass


class TaskRead(BaseModel):
    id: int
    description: str
    due_date: datetime
    priority: str
    user_id: Optional[int]

    class Config:
        orm_mode = True


class TimeEntryBase(BaseModel):
    start_at: datetime
    end_at: datetime

    class Config:
        orm_mode = True


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryRead(TimeEntryBase):
    id: int
    duration: float

    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    notify_before_minutes: int

    class Config:
        orm_mode = True


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    id: int

    class Config:
        orm_mode = True


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime
    roles: List[RoleRead] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
