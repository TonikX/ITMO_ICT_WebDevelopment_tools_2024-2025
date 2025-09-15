from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime

class UserBase(SQLModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = 1

class TaskCreate(TaskBase):
    category_ids: Optional[List[int]] = None  

class TaskRead(TaskBase):
    id: int
    user_id: int
    categories: List["CategoryRead"] = []  
    time_logs: List["TimeLogRead"] = []

class CategoryBase(SQLModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    tasks: List[TaskRead] = []  

class TimeLogBase(SQLModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

class TimeLogCreate(TimeLogBase):
    pass

class TimeLogRead(TimeLogBase):
    id: int
    task_id: int

class ScheduleBase(SQLModel):
    date: datetime
    description: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleRead(ScheduleBase):
    id: int
    user_id: int