from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApplicationBase(BaseModel):
    tournament_id: int
    team_id: int
    comment: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: str
    comment: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    application_id: int
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True
