from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel
from typing_extensions import List

from model.schemas.skill import SkillRead


class UserBase(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserPatch(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


class SkillWithExp(BaseModel):
    id: int
    name: str
    description: Optional[str]
    experience_years: Optional[int]

    class Config:
        from_attributes = True


class UserSkillRead(BaseModel):
    skill: SkillRead
    experience_years: Optional[int]

    class Config:
        from_attributes = True


class UserFullRead(UserBase):
    id: int
    created_at: datetime
    skills: List[UserSkillRead] = []


class UserPasswordChange(SQLModel):
    old_password: str
    new_password: str
