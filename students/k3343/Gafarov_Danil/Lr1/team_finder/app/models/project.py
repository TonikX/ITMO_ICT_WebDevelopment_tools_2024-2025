# app/models/project.py

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    deadline: str | None = None
    owner_id: int = Field(foreign_key="user.id")

    members_link: List["TeamMember"] = Relationship(back_populates="project")