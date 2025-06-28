from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    bio: Optional[str]
    experience: Optional[str]
    interests: Optional[str]

    skills: List["ProfileSkill"] = Relationship(back_populates="profile")
    projects_link: List["TeamMember"] = Relationship(back_populates="profile")
