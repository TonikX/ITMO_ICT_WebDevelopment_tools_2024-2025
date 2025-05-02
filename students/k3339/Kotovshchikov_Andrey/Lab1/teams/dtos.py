from datetime import date, datetime
from typing import Annotated, Optional

from sqlmodel import Field
from core.dtos import CoreDTO
from teams.models import Role, TaskStatus
from users.dtos import UserDTO


class TeamCreateDTO(CoreDTO):
    name: str


class TeamDTO(CoreDTO):
    id: int
    name: str
    created_at: datetime


class MemberDTO(CoreDTO):
    id: int
    user: UserDTO
    role: Role


class MemberAddDTO(CoreDTO):
    user_id: int
    role: Role


class TaskCreateDTO(CoreDTO):
    member_id: int
    description: Annotated[str, Field(max_length=500, default="")]
    deadline: Optional[date] = None


class TaskUpdateDTO(CoreDTO):
    status: Optional[TaskStatus] = None
    description: Annotated[Optional[str], Field(max_length=500)] = None


class TaskDTO(CoreDTO):
    id: int
    member: MemberDTO
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    deadline: Optional[date] = None
