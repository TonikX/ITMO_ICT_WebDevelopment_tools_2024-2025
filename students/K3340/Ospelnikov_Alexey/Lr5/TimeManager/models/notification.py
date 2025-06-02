from typing import Optional, List
from datetime import datetime
from models.task import Task
from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text


class NotificationDefault(SQLModel):
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False
    missed: Optional[bool] = True

class Notification(NotificationDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    parent_task: Optional[Task] = Relationship(back_populates="notification_list")
    

class NotificationTask(NotificationDefault):
    parent_task: Optional[Task] = None

    
