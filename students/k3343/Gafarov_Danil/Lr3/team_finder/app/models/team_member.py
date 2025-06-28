# app/models/team_member.py

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class TeamMember(SQLModel, table=True):
    profile_id: int = Field(foreign_key="profile.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)

    role: str  # Поле, характеризующее связь (например: "Backend Developer")
    joined_at: datetime = Field(default=datetime.now)

    profile: "Profile" = Relationship(back_populates="projects_link")
    project: "Project" = Relationship(back_populates="members_link")