from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class BudgetCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    budget_id: int = Field(foreign_key="budget.id")
    category_id: int = Field(foreign_key="category.id")
    limit_amount: float 
    period: Optional[str] = None  


    budget: Optional["Budget"] = Relationship(back_populates="category_links")
    category: Optional["Category"] = Relationship(back_populates="budget_links")