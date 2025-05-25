from pydantic import BaseModel


class BudgetBase(BaseModel):
    limit: float
    category_id: int


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    category_name: str

    class Config:
        from_attributes = True
