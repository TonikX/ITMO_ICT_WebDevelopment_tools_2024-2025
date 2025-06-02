from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from typing_extensions import List

from model.schemas.daily_schedule import DailyScheduleReadShort
from model.schemas.task import TaskReadShort


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserRead(UserBase):
    id: int
    tasks: List["TaskReadShort"] = []
    schedules: List["DailyScheduleReadShort"] = []
