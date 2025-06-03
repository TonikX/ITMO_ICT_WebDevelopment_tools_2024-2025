from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str

class UserRead(UserCreate):
    id: UUID
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

class TransactionRead(BaseModel):
    id: UUID
    account_id: UUID
    amount: int
    timestamp: datetime
    category: CategoryRead
    description: Optional[str]

    class Config:
        orm_mode = True
