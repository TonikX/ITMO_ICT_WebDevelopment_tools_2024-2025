from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class UserRole(Enum):
    user = "user"
    admin = "admin"

class TeamRole(Enum):
    designer = "designer"
    marketing = "marketing"
    programmer = "programmer"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    password: str
    phone: str
    role: UserRole = UserRole.user
    created_at: Optional[datetime] = datetime.now()

    participants: List["Participant"] = Relationship(back_populates="user")
    organized_hackathons: List["Hackathon"] = Relationship(back_populates="main_organizer")
    coordinators: List["Organizer"] = Relationship(back_populates="user")


class Hackathon(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    organizer_id: int = Field(default=None, foreign_key="user.id")

    main_organizer: Optional[User] = Relationship(back_populates="organized_hackathons")
    tasks: List["Task"] = Relationship(back_populates="hackathon")
    participants: List["Participant"] = Relationship(back_populates="hackathon")
    organizers: List["Organizer"] = Relationship(back_populates="hackathon")


class Organizer(SQLModel, table=True):
    hackathon_id: int = Field(default=None, foreign_key="hackathon.id", primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)

    hackathon: Optional["Hackathon"] = Relationship(back_populates="organizers")
    user: Optional["User"] = Relationship(back_populates="coordinators")


class Participant(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    hackathon_id: int = Field(default=None, foreign_key="hackathon.id")
    user_id: int = Field(default=None, foreign_key="user.id")
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    is_approved: bool = False

    hackathon: Optional[Hackathon] = Relationship(back_populates="participants")
    team: Optional["Team"] = Relationship(back_populates="members")
    user: Optional["User"] = Relationship(back_populates="participants")
    uploaded_tasks: List["UploadedTask"] = Relationship(back_populates="participant")


class Team(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    members: List[Participant] = Relationship(back_populates="team")
    uploaded_tasks: List["UploadedTask"] = Relationship(back_populates="team")



class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str
    requirements: str
    evaluation_criteria: str
    hackathon_id: int = Field(default=None, foreign_key="hackathon.id")

    hackathon: Optional[Hackathon] = Relationship(back_populates="tasks")
    uploaded_tasks: List["UploadedTask"] = Relationship(back_populates="task")


class UploadedTask(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    participant_id: Optional[int] = Field(default=None, foreign_key="participant.id")
    task_id: int = Field(default=None, foreign_key="task.id")
    rate: Optional[int]

    team: Optional[Team] = Relationship(back_populates="uploaded_tasks")
    participant: Optional[Participant] = Relationship(back_populates="uploaded_tasks")
    task: Optional[Task] = Relationship(back_populates="uploaded_tasks")
