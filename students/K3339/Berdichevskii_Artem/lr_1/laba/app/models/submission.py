from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Submission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    task_id: int = Field(foreign_key="task.id", nullable=True)

    dt_created: datetime = Field(default_factory=datetime.now)
    score: Optional[int] = None

    team: Optional["Team"] = Relationship(back_populates="submissions", sa_relationship_kwargs={'lazy': 'selectin'})
    task: Optional["Task"] =Relationship(back_populates="submissions", sa_relationship_kwargs={'lazy': 'selectin'})
    attachment: str
