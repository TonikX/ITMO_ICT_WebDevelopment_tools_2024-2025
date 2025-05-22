from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str
    bucket_url: str
    uploaded_at: datetime = Field(default_factory=datetime.now)

    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    task: Optional["Task"] = Relationship(back_populates="attachments", sa_relationship_kwargs={'lazy': 'selectin'})
