from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Category(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = ""

    # 一对多关系：1 分类 → N 交易
    transactions: List["Transaction"] = Relationship(back_populates="category")