from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="user")
    schedules: List["Schedule"] = Relationship(back_populates="user")

class TaskCategory(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)
    association_priority: int = Field(default=1)  

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    tasks: List["Task"] = Relationship(back_populates="categories", link_model=TaskCategory)  

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = Field(default=1)  # 1 - низкая, 5 - высокая
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tasks")
    categories: List[Category] = Relationship(back_populates="tasks", link_model=TaskCategory)  
    time_logs: List["TimeLog"] = Relationship(back_populates="task")

class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  
    task: Optional[Task] = Relationship(back_populates="time_logs")

class Schedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    date: datetime
    description: Optional[str] = None
    user: Optional[User] = Relationship(back_populates="schedules")