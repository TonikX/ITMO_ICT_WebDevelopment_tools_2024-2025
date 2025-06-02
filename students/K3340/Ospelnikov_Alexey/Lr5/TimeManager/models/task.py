from enum import Enum
from typing import Optional, List
from datetime import datetime

from .task_schedule import TaskSchedule
from .user import User

from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text


class PriorityType(Enum):
    extreme = "extreme"
    high = "high"
    medium = "medium"
    low = "low"


class StatusType(Enum):
    done = "done"
    in_progress = "in_progress"
    cancelled = "cancelled"
    delayed = "delayed"
    added = "added"


class TaskDefault(SQLModel):
    name: str
    description: Optional[str] = ""
    deadline: datetime
    status: StatusType
    priority: PriorityType
    tag: Optional[str] = ""
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    
    
class Task(TaskDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    schedules: Optional[List["Schedule"]] = Relationship(
        back_populates="tasks", link_model=TaskSchedule
    )    
    created_by: int = Field(
        default=None, foreign_key="user.id"
    )    
    author: Optional[User] = Relationship(back_populates="task_list")
    task_link: List[TaskSchedule] = Relationship(back_populates="tasks")
    notification_list: List["Notification"] = Relationship(back_populates="parent_task")
    
    

class TaskUser(TaskDefault):
    author: Optional[User] = None