from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str] = None
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
