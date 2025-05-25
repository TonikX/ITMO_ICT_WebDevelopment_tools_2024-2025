from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.user_model import User
    from models.time_entry_model import TimeEntry
    from models.task_assignment_model import TaskAssignment

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = Field(default=3, description="1 - высокий, 2 - средний, 3 - низкий")
    status: str = Field(default="Pending", description="Pending, In Progress, Completed")

    # Внешний ключ, указывающий на пользователя (создателя задачи).
    creator_id: int = Field(foreign_key="users.id", nullable=False)
    # Явное условие соединения для отношения с пользователем.
    creator: Optional["User"] = Relationship(
        back_populates="tasks_created",
        sa_relationship_kwargs={"primaryjoin": "Task.creator_id == User.id"}
    )

    time_entries: List["TimeEntry"] = Relationship(back_populates="task")
    assignments: List["TaskAssignment"] = Relationship(back_populates="task")


# Схемы для API по задачам

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = 3

class TaskRead(SQLModel):
    id: int
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[int]
    status: str
    creator_id: int

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None