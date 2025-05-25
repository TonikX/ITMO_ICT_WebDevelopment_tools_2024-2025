from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.task_model import Task
    from models.user_model import User

class TaskAssignment(SQLModel, table=True):
    __tablename__ = "task_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    # Дополнительное поле для описания роли пользователя в задаче
    role: str = Field(nullable=False)

    task: Optional["Task"] = Relationship(back_populates="assignments")
    user: Optional["User"] = Relationship(back_populates="assignments")


# Схемы для API по назначению задач

class TaskAssignmentCreate(SQLModel):
    task_id: int
    user_id: int
    role: str

class TaskAssignmentRead(SQLModel):
    id: int
    task_id: int
    user_id: int
    role: str