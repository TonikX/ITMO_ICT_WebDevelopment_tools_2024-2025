from pydantic import BaseModel
from datetime import date

class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float | None = 0.0
    target_date: date | None = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: str | None = None
    target_amount: float | None = None
    current_amount: float | None = None
    target_date: date | None = None

class GoalOut(GoalBase):
    goal_id: int
    user_id: int

    class Config:
        orm_mode = True