from pydantic import BaseModel
from typing import List, Optional

class ProfileBase(BaseModel):
    bio: Optional[str]
    experience: Optional[str]
    interests: Optional[str]

class ProfileCreate(BaseModel):
    user_id: int
    bio: str
    experience: str
    interests: str


class ProfileSkillOut(BaseModel):
    skill_id: int
    level: int

class ProfileOut(ProfileBase):
    id: int
    user_id: int
    skills: List[ProfileSkillOut] = []