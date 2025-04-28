import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr

from db.models import UserRole


class MessageResponse(BaseModel):
    status: int
    message: str


class BaseDataResponse(BaseModel):
    status: int
    data: Any


class NotFoundDataResponse(BaseDataResponse):
    pass


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserBodySchema(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole


class UserDataResponse(BaseDataResponse):
    data: UserResponse 