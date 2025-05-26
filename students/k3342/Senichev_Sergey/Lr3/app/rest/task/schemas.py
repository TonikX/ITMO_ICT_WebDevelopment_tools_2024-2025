import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from db.models import Priority, Status
from rest.shared_schemas import (
    MessageResponse,
    BaseDataResponse,
    NotFoundDataResponse,
    TaskResponse,
    TaskWithLinksResponse,
    SprintResponse
)


class TaskBodySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    summary: str
    priority: Priority
    description: Optional[str]
    planned_end_at: Optional[datetime.datetime]
    status: Status
    sprint_id: Optional[int]


# Response classes that reference the shared models
class TaskDataResponse(BaseDataResponse):
    data: TaskResponse


class TaskWithLinksDataResponse(BaseDataResponse):
    data: TaskWithLinksResponse 