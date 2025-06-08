from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
# 这里先不直接导入 Budget，避免循环导入

class BudgetExpenseLink(SQLModel, table=True):
    budget_id: int = Field(foreign_key="budget.id", primary_key=True)
    expense_id: int = Field(foreign_key="transaction.id", primary_key=True)
    spent_amount: float  # 中间表额外字段

    def get_budget(self):
        from .budget import Budget  # 在这里局部导入
        # 处理获取预算的逻辑
        budget = None
        return budget

    # 双向关联（延迟处理导入）
    budget: Optional["Budget"] = Relationship(back_populates="budget_expenses")
    expense: Optional["Transaction"] = Relationship(back_populates="budget_links")