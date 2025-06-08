from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .user import User  # 关联用户模型

class FinancialGoal(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    title: str
    target_amount: float
    current_amount: float = Field(default=0.0)
    deadline: datetime
    is_achieved: bool = Field(default=False)

    # 外键：关联用户
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="financial_goals")