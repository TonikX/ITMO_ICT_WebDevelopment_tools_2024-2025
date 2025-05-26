from sqlmodel import SQLModel, Field
from typing import Optional


class RealBook(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)  # Обязательное поле
    author: str = Field(nullable=False)
    year: Optional[int] = None
    publisher: Optional[str] = None
    description: Optional[str] = None