from datetime import datetime
from enum import StrEnum
from sqlalchemy import create_engine, DateTime, func, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "parsed_task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    summary: Mapped[str] = mapped_column(String(255))
    priority: Mapped[Priority] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[Status] = mapped_column(String(20))
    repository: Mapped[str] = mapped_column(String(255))
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), onupdate=func.now())

def create_db_and_tables(engine):
    Base.metadata.create_all(engine) 