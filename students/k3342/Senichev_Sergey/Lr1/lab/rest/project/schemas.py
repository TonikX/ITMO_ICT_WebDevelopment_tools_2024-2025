from datetime import datetime
from typing import Any, Optional, List

from pydantic import BaseModel, ConfigDict

from rest.sprint.schemas import SprintResponse


class MessageResponse(BaseModel):
    status: int
    message: str


class BaseDataResponse(BaseModel):
    status: int
    data: Any


class NotFoundDataResponse(BaseDataResponse):
    pass


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProjectWithSprints(Project):
    sprints: List["Sprint"] = []

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    sprints: list[SprintResponse]


class ProjectBodySchema(BaseModel):
    name: str
    description: str | None


class ProjectDataResponse(BaseDataResponse):
    data: ProjectResponse 