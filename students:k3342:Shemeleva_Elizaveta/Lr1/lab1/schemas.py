from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# задачи
class TaskBase(BaseModel):
    description: str
    due_date: datetime
    priority: str


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    time_entries: List["TimeEntryRead"] = []
    notifications: List["NotificationRead"] = []


# записи времени
class TimeEntryBase(BaseModel):
    start_at: datetime
    end_at: datetime


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryRead(TimeEntryBase):
    id: int
    duration: float


# уведомления
class NotificationBase(BaseModel):
    notify_before_minutes: int


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    id: int


# пользователи и роли
class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime
    roles: List[str] = []  # список имён ролей


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
