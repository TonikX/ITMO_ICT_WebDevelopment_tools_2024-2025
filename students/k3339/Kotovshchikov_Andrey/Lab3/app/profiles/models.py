from datetime import date
from enum import StrEnum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from core.models import CoreModel
from users.models import User


class SkillLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProfileSkill(SQLModel, table=True):
    profile_id: int = Field(
        foreign_key="profile.id",
        primary_key=True,
        ondelete="CASCADE",
    )

    skill_id: int = Field(
        foreign_key="skill.id",
        primary_key=True,
        ondelete="CASCADE",
    )

    level: SkillLevel = Field(default=SkillLevel.BEGINNER)


class Skill(CoreModel, table=True):
    name: str = Field(unique=True)

    profiles: Optional[list["Profile"]] = Relationship(
        back_populates="skills",
        link_model=ProfileSkill,
    )


class Profile(CoreModel, table=True):
    first_name: str
    last_name: str
    birthdate: date

    about_me: str
    work_experience: int

    user_id: int = Field(
        foreign_key="user.id",
        unique=True,
        ondelete="CASCADE",
    )

    user: Optional[User] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"},
    )

    skills: Optional[list["Skill"]] = Relationship(
        back_populates="profiles",
        link_model=ProfileSkill,
        sa_relationship_kwargs={"lazy": "selectin", "uselist": True},
    )
