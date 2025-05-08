from pydantic import BaseModel, EmailStr
from typing import Optional


class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int

    class Config:
        from_attributes = True

class SkillUpdate(SkillBase):
    name: Optional[str]
    description: Optional[str]

class UserShortInfo(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None

class UsersSkillReadDetail(BaseModel):
    user: Optional["UserShortInfo"]
    experience_years: Optional[int]
