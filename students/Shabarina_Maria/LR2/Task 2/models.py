from sqlmodel import SQLModel, Field


class News(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    title: str
    topic: str
    text: str
