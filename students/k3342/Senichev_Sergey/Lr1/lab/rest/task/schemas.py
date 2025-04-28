import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from db.models import Priority, Status, LinkStatus
from rest.comment.schemas import CommentResponse
from rest.sprint.schemas import SprintResponse
from rest.user.schemas import UserResponse


class MessageResponse(BaseModel):
    status: int
    message: str


class BaseDataResponse(BaseModel):
    status: int
    data: Any


class NotFoundDataResponse(BaseDataResponse):
    data: str


class TaskDataResponse(BaseDataResponse):
    data: "TaskResponse"


class TaskWithLinksDataResponse(BaseDataResponse):
    data: "TaskWithLinksResponse"


class TaskLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    parent_task_id: int
    child_task_id: int
    status: LinkStatus


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    summary: str
    priority: Priority
    description: str | None
    planned_end_at: datetime.datetime | None
    status: Status
    created_at: datetime.datetime
    updated_at: datetime.datetime

    sprint: SprintResponse | None
    assignee: UserResponse | None
    linked_tasks: list[TaskLinkResponse] | None
    comments: list[CommentResponse]


class TaskWithLinksResponse(TaskResponse):
    linked_tasks: list[TaskLinkResponse] | None


class TaskBodySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    summary: str
    priority: Priority
    description: str | None
    planned_end_at: datetime.datetime | None
    status: Status
    sprint_id: int | None
    assignee_id: int | None
