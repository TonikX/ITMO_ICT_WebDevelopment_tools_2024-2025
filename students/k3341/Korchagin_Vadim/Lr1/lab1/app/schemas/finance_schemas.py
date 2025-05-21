from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    email: str
    password: str 

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class CreateCategory(BaseModel):
    name: str

class CreateTransaction(BaseModel):
    user_id: int
    category_id: int
    account_id: Optional[int] = None
    amount: float
    description: Optional[str] = None

class CreateBudget(BaseModel):
    user_id: int
    category_id: int
    limit_amount: float

class CreateAccount(BaseModel):
    user_id: int
    name: str
    balance: float = 0.0

class CreateGoal(BaseModel):
    user_id: int
    title: str
    target_amount: float
    deadline: Optional[datetime] = None
    current_amount: float = 0.0


# Для чтения:
class ReadCategory(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class ReadTransaction(BaseModel):
    id: int
    amount: float
    description: Optional[str]
    created_at: datetime
    account_id: Optional[int] = None
    class Config:
        from_attributes = True

class ReadBudget(BaseModel):
    id: int
    limit_amount: float
    class Config:
        from_attributes = True

class ReadAccount(BaseModel):
    id: int
    name: str
    balance: float
    class Config:
        from_attributes = True

class ReadGoal(BaseModel):
    id: int
    title: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime]
    class Config:
        from_attributes = True
        
        
class CreateUserCategoryPreference(BaseModel):
    user_id: int
    category_id: int
    notification_enabled: bool = True

class ReadUserCategoryPreference(BaseModel):
    user_id: int
    category_id: int
    notification_enabled: bool
    class Config:
        from_attributes = True

# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------

class ReadUserWithRelations(UserOut):
    accounts: List[ReadAccount] = []
    transactions: List[ReadTransaction] = []
    budgets: List[ReadBudget] = []
    goals: List[ReadGoal] = []
    category_preferences: List[ReadUserCategoryPreference] = []

    class Config:
        from_attributes = True


class ReadAccountWithTransactions(ReadAccount):
    transactions: List[ReadTransaction] = []

    class Config:
        from_attributes = True

class ReadCategoryWithUsers(ReadCategory):
    user_preferences: List[ReadUserCategoryPreference] = []

    class Config:
        from_attributes = True


class ReadGoalWithUser(ReadGoal):
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True



class ReadBudgetFull(ReadBudget):
    user: Optional[UserOut] = None
    category: Optional[ReadCategory] = None

    class Config:
        from_attributes = True



class ReadTransactionFull(ReadTransaction):
    user: Optional[UserOut] = None
    category: Optional[ReadCategory] = None
    account: Optional[ReadAccount] = None

    class Config:
        from_attributes = True





