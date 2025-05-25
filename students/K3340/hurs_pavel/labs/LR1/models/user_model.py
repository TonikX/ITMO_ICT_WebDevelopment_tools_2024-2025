from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.task_model import Task
    from models.time_entry_model import TimeEntry
    from models.task_assignment_model import TaskAssignment

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    bio: Optional[str] = None

    tasks_created: List["Task"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"primaryjoin": "User.id == Task.creator_id"}
    )
    assignments: List["TaskAssignment"] = Relationship(back_populates="user")
    time_entries: List["TimeEntry"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str
    email: str
    bio: Optional[str] = None

class UserLogin(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None

class UserUpdatePassword(SQLModel):
    old_password: str
    new_password: str