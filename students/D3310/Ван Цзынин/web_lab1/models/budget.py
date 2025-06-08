from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .user import User

class Budget(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    category: str
    amount: float
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="budgets")

    def get_budget_expenses(self):
        from .budget_expense_link import BudgetExpenseLink  # 在这里局部导入
        # 处理与预算消费关联的逻辑
        budget_expenses = []
        return budget_expenses

    # 一对多关系：关联多对多中间表（延迟处理导入）
    budget_expenses: List["BudgetExpenseLink"] = Relationship(back_populates="budget")