from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    fullname: str
    hash_password: str
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    task_list: List["Task"] = Relationship(back_populates="author")