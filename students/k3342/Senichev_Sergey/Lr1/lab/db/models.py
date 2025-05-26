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

class Base(DeclarativeBase):
    pass


class Sprint(Base):
    __tablename__ = "sprint"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    start_at: Mapped[datetime.datetime]
    end_at: Mapped[datetime.datetime]

    tasks: Mapped[list["Task"]] = relationship(back_populates="sprint", lazy="raise")


class TaskLink(Base):
    __tablename__ = "task_link"

    parent_task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)
    parent_task: Mapped["Task"] = relationship(primaryjoin="Task.id==TaskLink.parent_task_id", lazy="raise")

    child_task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)
    child_task: Mapped["Task"] = relationship(primaryjoin="Task.id==TaskLink.child_task_id", lazy="raise")

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

    sprint_id: Mapped[int | None] = mapped_column(ForeignKey("sprint.id"))
    sprint: Mapped[Sprint | None] = relationship(back_populates="tasks", lazy="raise")

    linked_tasks: Mapped[list[TaskLink] | None] = relationship(primaryjoin=id == TaskLink.parent_task_id, lazy="raise")


def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
