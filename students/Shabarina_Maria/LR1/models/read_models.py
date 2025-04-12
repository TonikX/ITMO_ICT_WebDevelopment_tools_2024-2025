from sqlmodel import SQLModel
from datetime import date
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class UserSkillRead(SQLModel):
    id: int
    level: int
    user_id: int
    skill_id: int
    user_name: str
    skill_title: str


class UserPositionRead(SQLModel):
    id: int
    experience: int
    user_id: int
    position_id: int
    user_name: str
    position_title: str


class ParticipationRead(SQLModel):
    id: int
    user_id: int
    project_id: int
    user_name: str
    project_title: str


class UserTasksRead(SQLModel):
    id: int
    description: str
    deadline: date
    status: TaskStatus
    project_title: str


class ProjectParticipantsRead(SQLModel):
    id: int
    user_id: int
    user_name: str