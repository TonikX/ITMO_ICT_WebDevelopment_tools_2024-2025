from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

class Goal(SQLModel, table=True):
    __tablename__ = "goal"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    target_amount: Decimal
    current_amount: Decimal = 0
    due_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="goals")