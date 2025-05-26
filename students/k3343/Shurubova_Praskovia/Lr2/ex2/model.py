from sqlmodel import SQLModel, Field
from typing import Optional


class RealBook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    author: str = Field(index=True)
    year: int
    publisher: str
    description: str = Field(default="Описание недоступно")
