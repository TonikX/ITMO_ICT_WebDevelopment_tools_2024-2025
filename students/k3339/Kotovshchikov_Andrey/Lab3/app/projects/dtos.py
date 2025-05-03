from datetime import date
from typing import Optional
from core.dtos import CoreDTO


class ProjectBaseDTO(CoreDTO):
    name: str
    description: str
    deadline: Optional[date] = None


class ProjectCreateDTO(ProjectBaseDTO): ...


class ProjectDTO(ProjectBaseDTO):
    id: int


class ProjectUpdateDTO(ProjectBaseDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
