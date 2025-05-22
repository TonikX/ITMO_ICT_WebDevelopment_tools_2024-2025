from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AttachmentDisplay(BaseModel):
    id: int
    file_name: str
    bucket_url: str
    uploaded_at: datetime


class TaskBase(BaseModel):
    task_name: str
    task_description: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskDisplay(TaskBase):
    id: int
    attachments: Optional[List[AttachmentDisplay]]
