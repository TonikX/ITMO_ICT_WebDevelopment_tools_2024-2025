
from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text
	

class TaskScheduleDefault(SQLModel):
    urgency: Optional[int] = 5
    start_time: datetime
    end_time: Optional[datetime]

class TaskSchedule(TaskScheduleDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(
            default=None, foreign_key="task.id"
        )
    schedule_id: Optional[int] = Field(
        default=None, foreign_key="schedule.id"
    )   
    tasks: Optional["Task"] = Relationship(back_populates="task_link")
    schedules: Optional["Schedule"] = Relationship(back_populates="schedule_link")

class TaskScheduleSerializator(TaskScheduleDefault):
    tasks: Optional["Task"] = None
    schedules: Optional["Schedule"] = None
    
