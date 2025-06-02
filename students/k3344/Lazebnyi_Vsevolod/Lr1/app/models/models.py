from pydantic import BaseModel
from typing import Optional
import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    status: str
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str
    type: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    status: str
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: float
    date: datetime.date
    description: Optional[str] = None
    status: Optional[str] = "completed"

class TransactionCreate(TransactionBase):
    category_id: int

class TransactionRead(TransactionBase):
    id: int
    user_id: int
    category_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class BudgetBase(BaseModel):
    limit_amount: float
    start_date: datetime.date
    end_date: datetime.date

class BudgetCreate(BudgetBase):
    category_id: int

class BudgetRead(BudgetBase):
    id: int
    user_id: int
    category_id: int
    status: str
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class GoalBase(BaseModel):
    title: str
    target_amount: float
    current_amount: float = 0
    deadline: datetime.date
    status: Optional[str] = "active"

class GoalCreate(GoalBase):
    pass

class GoalRead(GoalBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    type: str
    status: Optional[str] = "unread"

class NotificationCreate(NotificationBase):
    budget_id: int

class NotificationRead(NotificationBase):
    id: int
    user_id: int
    budget_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True