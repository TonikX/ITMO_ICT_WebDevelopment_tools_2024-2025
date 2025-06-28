# app/schemas/project.py

from pydantic import BaseModel
from typing import List

class TeamMemberOut(BaseModel):
    profile_id: int
    role: str
    joined_at: str

class ProjectCreate(BaseModel):
    title: str
    description: str
    deadline: str | None = None
    owner_id: int

class ProjectOut(ProjectCreate):
    id: int
    members: List[TeamMemberOut] = []