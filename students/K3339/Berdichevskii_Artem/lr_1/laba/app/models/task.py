from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_name: str
    task_description: str

    event_id: int = Field(foreign_key="event.id")
    event: Optional["Event"] = Relationship(back_populates="tasks")

    attachments: List["Attachment"] = Relationship(back_populates="task", sa_relationship_kwargs={'lazy': 'selectin'})
    submissions: List["Submission"] = Relationship(back_populates="task", sa_relationship_kwargs={'lazy': 'selectin'})
