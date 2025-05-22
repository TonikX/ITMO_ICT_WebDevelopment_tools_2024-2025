from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.registration import TeamDisplay
from app.schemas.task import TaskDisplay


class SubmissionBase(BaseModel):
    attachment: str


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionSchema(SubmissionBase):
    id: int
    team: TeamDisplay
    task: TaskDisplay
    dt_created: datetime = None
    score: Optional[int]
