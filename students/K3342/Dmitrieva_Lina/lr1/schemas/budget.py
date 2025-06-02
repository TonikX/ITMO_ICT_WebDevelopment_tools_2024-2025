from pydantic import BaseModel

class BudgetCreate(BaseModel):
    user_id: int
    month: int
    year: int
    amount: float

class BudgetRead(BaseModel):
    id: int
    user_id: int
    month: int
    year: int
    amount: float

    class Config:
        from_attributes = True
