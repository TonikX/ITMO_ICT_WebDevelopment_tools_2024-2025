from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Skill(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    profiles: List["ProfileSkill"] = Relationship(back_populates="skill")



