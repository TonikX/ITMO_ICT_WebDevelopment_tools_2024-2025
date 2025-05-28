from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.user_model import User
    from models.task_model import Task

class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    duration: int = Field(nullable=False, description="Длительность в минутах")
    entry_date: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[str] = None

    task: Optional["Task"] = Relationship(back_populates="time_entries")
    user: Optional["User"] = Relationship(back_populates="time_entries")



class TimeEntryCreate(SQLModel):
    task_id: int
    duration: int
    comment: Optional[str] = None

class TimeEntryRead(SQLModel):
    id: int
    task_id: int
    user_id: int
    duration: int
    entry_date: datetime
    comment: Optional[str] = None

class TimeEntryUpdate(SQLModel):
    duration: Optional[int] = None
    comment: Optional[str] = None