from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password: str

    def get_transactions(self):
        from .transaction import Transaction  # 在这里导入，而不是在顶层
        # 处理与交易相关的逻辑
        transactions = []
        return transactions

    # 一对多关系：1 用户 → N 预算
    budgets: List["Budget"] = Relationship(back_populates="user")

    # 一对多关系：1 用户 → N 财务目标
    financial_goals: List["FinancialGoal"] = Relationship(back_populates="user")