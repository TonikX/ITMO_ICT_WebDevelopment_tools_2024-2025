from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from db.models import Priority, Status


class MessageResponse(BaseModel):
    status: int
    message: str


class BaseDataResponse(BaseModel):
    status: int
    data: Any


class NotFoundDataResponse(BaseDataResponse):
    data: str


class SprintDataResponse(BaseDataResponse):
    data: "SprintResponse"


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: int
    summary: str
    priority: Priority
    description: str | None
    planned_end_at: datetime | None
    status: Status
    created_at: datetime
    updated_at: datetime


class SprintBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    project_id: int


class SprintCreate(SprintBase):
    pass


class SprintUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    project_id: int | None = None


class Sprint(SprintBase):
    id: int

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class SprintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: int
    title: str
    start_at: datetime
    end_at: datetime
    project_id: int

    tasks: list[TaskResponse]


class SprintBodySchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    project_id: int
