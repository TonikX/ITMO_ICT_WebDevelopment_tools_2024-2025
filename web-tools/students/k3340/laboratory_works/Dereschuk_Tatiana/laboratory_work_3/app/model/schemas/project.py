from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from model.schemas.user import UserFullRead


class ProjectBase(BaseModel):
    title: str
    description: str
    goals: str
    expected_outcomes: str
    deadline: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[str] = None
    expected_outcomes: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectRead(ProjectBase):
    id: int
    owner: UserFullRead

    class Config:
        from_attributes = True