from pydantic import BaseModel
import datetime
from typing import List, Optional
import enum

class TransactionTypeEnum(str, enum.Enum):
    income = "income"
    expense = "expense"

class AccountBase(BaseModel):
    name: str
    balance: Optional[float] = 0.0

class AccountCreate(AccountBase):
    pass

class AccountUpdate(AccountBase):
    pass

class AccountOut(AccountBase):
    id: int
    user_id: int
    transactions: List['TransactionOut'] = []
    class Config:
        orm_mode = True

class TransactionCategoryBase(BaseModel):
    allocated_amount: float

class TransactionCategoryCreate(TransactionCategoryBase):
    category_id: int

class TransactionCategoryOut(TransactionCategoryBase):
    category: 'CategoryOut'
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    account_id: int
    amount: float
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    type: TransactionTypeEnum

class TransactionCreate(TransactionBase):
    categories: List[TransactionCategoryCreate] = []

class TransactionUpdate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    user_id: int
    transaction_categories: List[TransactionCategoryOut] = []
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    class Config:
        orm_mode = True

class BudgetBase(BaseModel):
    category_id: int
    period: str
    limit_amount: float
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BudgetBase):
    pass

class BudgetOut(BudgetBase):
    id: int
    user_id: int
    category: CategoryOut
    class Config:
        orm_mode = True

class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: Optional[float] = 0.0
    due_date: Optional[datetime.date] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    pass

class GoalOut(GoalBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class ExpenseAnalysisOut(BaseModel):
    category: str
    total_expense: float
    class Config:
        orm_mode = True

class BudgetNotificationOut(BaseModel):
    category: str
    budget_limit: float
    spent_amount: float
    notification: str
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    title: str
    message: str

class NotificationOut(NotificationBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_savings: float
    class Config:
        orm_mode = True

class SpendingTrend(BaseModel):
    month: str
    total_expense: float
    class Config:
        orm_mode = True

AccountOut.update_forward_refs()
TransactionOut.update_forward_refs()
TransactionCategoryOut.update_forward_refs()
CategoryOut.update_forward_refs()
BudgetOut.update_forward_refs()
GoalOut.update_forward_refs()
