from typing import Optional
from sqlmodel import SQLModel, Field


class BookParsed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author: str
    title: str
    description: Optional[str]
