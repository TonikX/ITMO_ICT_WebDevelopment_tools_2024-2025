from enum import Enum
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    due_date: datetime
    priority: PriorityEnum
    created_at: datetime = Field(default_factory=datetime.utcnow)
