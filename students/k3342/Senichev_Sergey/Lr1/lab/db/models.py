import datetime
from enum import StrEnum

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from db.database import engine

class Priority(StrEnum):
    trivial = "trivial"
    blocker = "blocker"
    critical = "critical"
    major = "major"
    minor = "minor"


class Status(StrEnum):
    open = "open"
    in_progress = "in_progress"
    done = "done"


class LinkStatus(StrEnum):
    is_blocked_by = "is_blocked_by"
    blocks = "blocks"


class UserRole(StrEnum):
    admin = "admin"
    developer = "developer"
    manager = "manager"
    viewer = "viewer"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    full_name: Mapped[str]
    role: Mapped[UserRole]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())

    assigned_tasks: Mapped[list["Task"]] = relationship(back_populates="assignee", lazy="select")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author", lazy="select")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())

    sprints: Mapped[list["Sprint"]] = relationship(back_populates="project", lazy="select")


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    start_at: Mapped[datetime.datetime]
    end_at: Mapped[datetime.datetime]
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="sprints", lazy="select")

    tasks: Mapped[list["Task"]] = relationship(back_populates="sprint", lazy="select")


class TaskLink(Base):
    __tablename__ = "task_link"

    parent_task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)
    parent_task: Mapped["Task"] = relationship(primaryjoin="Task.id==TaskLink.parent_task_id", lazy="select")

    child_task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)
    child_task: Mapped["Task"] = relationship(primaryjoin="Task.id==TaskLink.child_task_id", lazy="select")

    status: Mapped[LinkStatus]


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    summary: Mapped[str]
    priority: Mapped[Priority]
    description: Mapped[str | None]
    planned_end_at: Mapped[datetime.datetime | None]
    status: Mapped[Status]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())

    sprint_id: Mapped[int | None] = mapped_column(ForeignKey("sprints.id"))
    sprint: Mapped[Sprint | None] = relationship(back_populates="tasks", lazy="select")

    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    assignee: Mapped[User | None] = relationship(back_populates="assigned_tasks", lazy="select")

    linked_tasks: Mapped[list[TaskLink] | None] = relationship(primaryjoin=id == TaskLink.parent_task_id, lazy="select")
    comments: Mapped[list["Comment"]] = relationship(back_populates="task", lazy="select")


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    task: Mapped[Task] = relationship(back_populates="comments", lazy="select")

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped[User] = relationship(back_populates="comments", lazy="select")


def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
