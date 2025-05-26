import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from rest.shared_schemas import (
    MessageResponse,
    BaseDataResponse,
    NotFoundDataResponse,
    TaskResponse,
    SprintWithTasksResponse
)


class SprintBodySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    start_at: datetime.datetime
    end_at: datetime.datetime


# Response classes that reference the shared models
class SprintDataResponse(BaseDataResponse):
    data: SprintWithTasksResponse 