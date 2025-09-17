from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime
from enum import Enum

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class NotificationType(str, Enum):
    over_budget = "over_budget"
    goal_achieved = "goal_achieved"
    goal_progress = "goal_progress"
    info = "info"

class NotificationStatus(str, Enum):
    unread = "unread"
    read = "read"

class LoginRequest(BaseModel):
    username: str
    password: str
    
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    status: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead
    
class CategoryBase(BaseModel):
    name: str
    type: CategoryType

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    user_id: int
    status: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: float
    date: datetime.date
    description: Optional[str] = None
    status: str = "completed"

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
    status: str = "active"

class BudgetCreate(BudgetBase):
    category_id: int

class BudgetRead(BudgetBase):
    id: int
    user_id: int
    category_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class GoalBase(BaseModel):
    title: str
    target_amount: float
    current_amount: float = 0
    deadline: datetime.date
    status: str = "active"

class GoalCreate(GoalBase):
    pass

class GoalRead(GoalBase):
    id: int
    user_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.unread

class NotificationCreate(NotificationBase):
    budget_id: Optional[int] = None
    goal_id: Optional[int] = None

class NotificationRead(NotificationBase):
    id: int
    user_id: int
    budget_id: Optional[int]
    goal_id: Optional[int]
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# News models
class NewsArticleBase(BaseModel):
    url: str
    title: str
    topic: str          # Новое поле для рубрики/темы
    text: str
class NewsArticleCreate(NewsArticleBase):
    pass
class NewsArticleRead(NewsArticleBase):
    id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True
        
class CategoryReadWithTransactions(CategoryRead):
    transactions: List[TransactionRead] = []