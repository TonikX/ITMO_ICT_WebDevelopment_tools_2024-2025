from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text

class News(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True, sa_column_kwargs={"unique": True})
    title: str
    topic: str
    text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)