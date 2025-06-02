from pydantic import BaseModel, validator
from datetime import date
from app.schemas.category import CategoryOut

class BudgetBase(BaseModel):
    category_id: int
    amount: float
    start_date: date
    end_date: date

    @validator("end_date")
    def validate_dates(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v

class BudgetCreate(BudgetBase):
    pass

class BudgetOut(BudgetBase):
    budget_id: int
    user_id: int
    category: CategoryOut

    class Config:
        from_attributes = True

class BudgetUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None

    @validator("end_date")
    def validate_dates(cls, v, values):
        if "start_date" in values and v and values["start_date"] and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v