from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    transactions: List["TransactionTag"] = Relationship(back_populates="tag")
