from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    period_start: date
    period_end: date
    user_id: int = Field(foreign_key="user.id")

    category_links: List["BudgetCategoryLink"] = Relationship(back_populates="budget")

class BudgetCategoryLink(SQLModel, table=True):
    budget_id:   int     = Field(foreign_key="budget.id", primary_key=True)
    category_id: int     = Field(foreign_key="category.id", primary_key=True)
    planned_amount: float

    budget:   Budget    = Relationship(back_populates="category_links")
    category: "Category" = Relationship()

