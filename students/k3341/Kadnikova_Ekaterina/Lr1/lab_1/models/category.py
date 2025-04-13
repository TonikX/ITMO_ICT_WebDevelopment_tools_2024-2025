from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_income: bool = False

    transactions: List["Transaction"] = Relationship(back_populates="category")
    budget_categories: List["BudgetCategory"] = Relationship(back_populates="category")