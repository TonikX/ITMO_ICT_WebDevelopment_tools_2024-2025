from enum import Enum
from typing import Optional, List
from datetime import datetime

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
    

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    fullname: str
    hash_password: str
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    task_list: List["Task"] = Relationship(back_populates="author")


class Task_Schedule_Default(SQLModel):
    urgency: Optional[int] = 5
    start_time: datetime
    end_time: Optional[datetime]

class Task_Schedule(Task_Schedule_Default, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(
            default=None, foreign_key="task.id"
        )
    schedule_id: Optional[int] = Field(
        default=None, foreign_key="schedule.id"
    )   
    tasks: Optional["Task"] = Relationship(back_populates="task_link")
    schedules: Optional["Schedule"] = Relationship(back_populates="schedule_link")

class Task_Schedule_Serializator(Task_Schedule_Default):
    tasks: Optional["Task"] = None
    schedules: Optional["Schedule"] = None

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
        back_populates="tasks", link_model=Task_Schedule
    )    
    created_by: int = Field(
        default=None, foreign_key="user.id"
    )    
    author: Optional[User] = Relationship(back_populates="task_list")
    task_link: List[Task_Schedule] = Relationship(back_populates="tasks")
    
    

class TaskUser(TaskDefault):
    author: Optional[User] = None
    

class Notification(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False
    
    
class Schedule(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: datetime
    tasks: Optional[List["Task"]] = Relationship(
        back_populates="schedules", link_model=Task_Schedule
    )
    productivity_score: Optional[int] = 5
    notes: Optional[str] = ''
    schedule_link: List[Task_Schedule] = Relationship(back_populates="schedules")
    
    

