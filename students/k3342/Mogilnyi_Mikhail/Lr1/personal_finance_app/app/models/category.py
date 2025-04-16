from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    transactions: List["Transaction"] = Relationship(back_populates="category")
