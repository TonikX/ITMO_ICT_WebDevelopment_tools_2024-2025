from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from models.models import UserRole


class UserCreate(SQLModel):
    name: str
    email: EmailStr
    password: str = Field(max_length=256, min_length=6)
    phone: str
    role: UserRole


class UserPatch(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = UserRole.user


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserReadShort(SQLModel):
    id: int
    name: str


class UserRead(SQLModel):
    id: int
    name: str
    email: str
    phone: str
    role: UserRole


class UserPasswordChange(SQLModel):
    old_password: str
    new_password: str
