from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from model.models.models import ProjectRole
from model.schemas.user import UserFullRead


class TeamMemberCreate(BaseModel):
    team_id: int
    user_id: int
    role: ProjectRole

class TeamMemberRead(BaseModel):
    team_id: int
    user: UserFullRead
    role: ProjectRole
    joined_at: datetime

    class Config:
        from_attributes = True

class TeamMemberUpdate(BaseModel):
    role: Optional[ProjectRole] = None