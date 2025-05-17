from pydantic import BaseModel
from typing import Optional

class GoalBase(BaseModel):
    user_id: int
    title: str
    amount: float
    description: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalRead(GoalBase):
    id: int

    class Config:
        orm_mode = True