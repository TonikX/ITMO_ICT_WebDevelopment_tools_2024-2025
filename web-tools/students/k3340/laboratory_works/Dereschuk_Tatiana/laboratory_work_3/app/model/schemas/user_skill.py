from typing import Optional

from pydantic import BaseModel


class UserSkillCreate(BaseModel):
    user_id: int
    skill_id: int
    experience_years: Optional[int] = 0


class UserSkillRead(BaseModel):
    user_id: int
    skill_id: int
    experience_years: Optional[int]

    class Config:
        from_attributes = True


class UserSkillUpdate(BaseModel):
    experience_years: Optional[int]
