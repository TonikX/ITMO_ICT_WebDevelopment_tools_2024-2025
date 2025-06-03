from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, SecretStr


class UserCreate(BaseModel):
    username: str
    email: str
    password: SecretStr

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

class AccountCreate(BaseModel):
    name: str
    balance: int
    currency: str

class AccountRead(AccountCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryRead(CategoryCreate):
    id: UUID

    class Config:
        orm_mode = True

class TransactionWrite(BaseModel):
    account_id: UUID
    amount: int
    category_id: UUID
    description: Optional[str]

class TransactionRead(BaseModel):
    id: UUID
    account_id: UUID
    amount: int
    timestamp: datetime
    category: CategoryRead
    description: Optional[str]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BudgetRead(BaseModel):
    id: UUID
    account_id: UUID
    limit: int
    start_date: datetime
    end_date: datetime

    class Config:
        orm_mode = True

class BudgetCreate(BaseModel):
    account_id: UUID
    limit: int
    start_date: datetime
    end_date: datetime

    class Config:
        orm_mode = True

class TargetCreate(BaseModel):
    account_id: UUID
    name: str
    target_amount: int
    deadline: datetime
    description: Optional[str] = None

    class Config:
        orm_mode = True


class TargetRead(TargetCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
