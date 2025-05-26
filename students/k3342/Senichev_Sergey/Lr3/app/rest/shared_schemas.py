import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict

from db.models import Priority, Status, LinkStatus


class MessageResponse(BaseModel):
    status: int
    message: str


class BaseDataResponse(BaseModel):
    status: int
    data: Any


class NotFoundDataResponse(BaseDataResponse):
    data: str


class SprintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_at: datetime.datetime
    end_at: datetime.datetime


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    summary: str
    priority: Priority
    description: Optional[str]
    planned_end_at: Optional[datetime.datetime]
    status: Status
    created_at: datetime.datetime
    updated_at: datetime.datetime

    sprint: Optional[SprintResponse]


class TaskLinkBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_task: TaskResponse
    status: LinkStatus


class TaskWithLinksResponse(TaskResponse):
    linked_tasks: Optional[List[TaskLinkBaseResponse]]


class SprintWithTasksResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_at: datetime.datetime
    end_at: datetime.datetime

    tasks: List[TaskResponse] 