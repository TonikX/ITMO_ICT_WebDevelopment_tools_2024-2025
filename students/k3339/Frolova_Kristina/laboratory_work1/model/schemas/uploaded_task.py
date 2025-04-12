from typing import Optional

from sqlmodel import SQLModel

class UploadedTaskBase(SQLModel):
    task_id: int
    participant_id: Optional[int] = None
    team_id: Optional[int] = None
    rate: Optional[int] = None

class TeamShort(SQLModel):
    id: int
    name: str

class ParticipantShort(SQLModel):
    id: int
    user_id: int

class TaskShort(SQLModel):
    id: int
    description: str

class UploadedTaskCreate(UploadedTaskBase):
    pass

class UploadedTaskRead(UploadedTaskBase):
    id: int
    team: Optional[TeamShort] = None
    participant: Optional[ParticipantShort] = None
    task: Optional[TaskShort] = None

class UploadedTaskUpdate(SQLModel):
    rate: Optional[int] = None
    participant_id: Optional[int] = None
    team_id: Optional[int] = None
