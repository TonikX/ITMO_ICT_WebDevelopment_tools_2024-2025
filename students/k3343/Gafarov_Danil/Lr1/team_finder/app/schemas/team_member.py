# app/schemas/team_member.py

from pydantic import BaseModel

class TeamMemberBase(BaseModel):
    profile_id: int
    project_id: int
    role: str

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberOut(TeamMemberBase):
    joined_at: str