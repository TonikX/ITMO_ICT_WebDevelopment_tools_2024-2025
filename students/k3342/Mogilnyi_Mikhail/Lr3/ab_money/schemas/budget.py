from typing import List
from sqlmodel import SQLModel
from datetime import date

class BudgetCategoryBase(SQLModel):
    category_id: int
    planned_amount: float

class BudgetCreate(SQLModel):
    name: str
    period_start: date
    period_end: date
    planned: List[BudgetCategoryBase] = []

class BudgetRead(SQLModel):
    id: int
    name: str
    period_start: date
    period_end: date
    planned: List[BudgetCategoryBase] = []
