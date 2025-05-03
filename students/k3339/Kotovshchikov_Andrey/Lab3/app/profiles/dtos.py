from datetime import date
from typing import Annotated, Optional

from pydantic import PositiveInt
from sqlmodel import Field
from core.dtos import CoreDTO
from users.dtos import UserDTO


class SkillDTO(CoreDTO):
    id: int
    name: str


class ProfileBaseDTO(CoreDTO):
    first_name: str
    last_name: str
    birthdate: date

    about_me: Annotated[str, Field(max_length=500)]
    work_experience: Annotated[int, Field(ge=0)]  # number of months


class ProfileCreateDTO(ProfileBaseDTO): ...


class ProfileUpdateDTO(CoreDTO):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[date] = None

    about_me: Annotated[Optional[str], Field(max_length=500)] = None
    work_experience: Annotated[Optional[int], Field(ge=0)] = None


class ProfileDTO(ProfileBaseDTO):
    user: UserDTO
    skills: Annotated[list[SkillDTO], Field(default_factory=list)]


class ProfileListDTO(CoreDTO):
    total: int
    profiles: list[ProfileDTO]


class CriteriaDTO(CoreDTO):
    skills: list[str]
    work_experience: int
    interests: list[str]
