import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from rest.user.schemas import UserResponse


class MessageResponse(BaseModel):
    status: int
    message: str


class BaseDataResponse(BaseModel):
    status: int
    data: Any


class NotFoundDataResponse(BaseDataResponse):
    pass


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: UserResponse


class CommentBodySchema(BaseModel):
    content: str
    task_id: int
    author_id: int


class CommentDataResponse(BaseDataResponse):
    data: CommentResponse 