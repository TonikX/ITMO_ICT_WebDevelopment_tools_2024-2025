from sqlmodel import SQLModel, Field, create_engine
from typing import Optional


class BookDefault(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: str
    published_year: int


engine = create_engine("sqlite:///books.db")
SQLModel.metadata.create_all(engine)
