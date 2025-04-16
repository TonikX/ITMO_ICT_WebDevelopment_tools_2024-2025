from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BudgetBase(BaseModel):
    user_id: int
    category_id: int
    limit: float
    period_start: datetime
    period_end: datetime

class BudgetCreate(BudgetBase):
    pass

class BudgetRead(BudgetBase):
    id: int

    class Config:
        orm_mode = True

class BudgetUpdate(BaseModel):
    limit: Optional[float] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
