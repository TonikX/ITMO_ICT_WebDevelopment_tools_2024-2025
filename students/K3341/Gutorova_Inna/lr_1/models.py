from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Enums
class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


# User models
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str



class UserRegister(SQLModel):
    username: str
    email: str
    password: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    categories: List["TaskCategory"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")
    tags: List["Tag"] = Relationship(back_populates="user")

    def verify_password(self, plain_password: str):
        return pwd_context.verify(plain_password, self.hashed_password)


class UserRead(UserBase):
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


# Task Category models
class TaskCategoryBase(SQLModel):
    name: str = Field(index=True)
    color_code: str = Field(default="#FFFFFF")


class TaskCategoryCreate(TaskCategoryBase):
    pass


class TaskCategory(TaskCategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="categories")
    tasks: List["Task"] = Relationship(back_populates="category")


class TaskCategoryRead(TaskCategoryBase):
    id: int
    user_id: int


# Task-Tag association
class TaskTagBase(SQLModel):
    task_id: int = Field(foreign_key="task.id")
    tag_id: int = Field(foreign_key="tag.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    is_primary: bool = False


class TaskTag(TaskTagBase, table=True):
    # Убираем id и делаем составной первичный ключ из task_id и tag_id
    __tablename__ = "tasktag"  # явно указываем имя таблицы
    task_id: int = Field(primary_key=True, foreign_key="task.id")
    tag_id: int = Field(primary_key=True, foreign_key="tag.id")
    # Остальные поля остаются без изменений
    added_at: datetime = Field(default_factory=datetime.utcnow)
    is_primary: bool = False


# Task models
class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: str
    deadline: Optional[datetime] = None
    priority: Priority = Priority.medium
    status: Status = Status.todo
    estimated_time_minutes: int = 0
    actual_time_minutes: int = 0


class TaskCreate(TaskBase):
    category_id: Optional[int] = None


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="taskcategory.id")

    user: User = Relationship(back_populates="tasks")
    category: Optional[TaskCategory] = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTag)
    reminders: List["Reminder"] = Relationship(back_populates="task")


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    user_id: int
    category_id: Optional[int]


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    estimated_time_minutes: Optional[int] = None
    actual_time_minutes: Optional[int] = None
    category_id: Optional[int] = None


class TaskWithTags(TaskRead):
    tags: List["TagRead"] = []


# Tag models
class TagBase(SQLModel):
    name: str = Field(index=True)


class TagCreate(TagBase):
    pass


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tags")
    tasks: List[Task] = Relationship(back_populates="tags", link_model=TaskTag)


class TagRead(TagBase):
    id: int
    user_id: int


# Reminder models
class ReminderBase(SQLModel):
    remind_at: datetime
    is_sent: bool = False


class ReminderCreate(ReminderBase):
    task_id: int


class Reminder(ReminderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="reminders")


class ReminderRead(ReminderBase):
    id: int
    task_id: int


# Добавим в конец models.py

class UserLogin(BaseModel):
    username: str
    password: str


class UserPassword(BaseModel):
    old_password: str
    new_password: str


class UserReadWithTasks(UserRead):
    tasks: List[TaskRead] = []
    categories: List[TaskCategoryRead] = []
    tags: List[TagRead] = []
    reminders: List[ReminderRead] = []
