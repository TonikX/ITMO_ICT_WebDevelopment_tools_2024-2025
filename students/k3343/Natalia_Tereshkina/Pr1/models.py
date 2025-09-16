from typing import List, Optional
from pydantic import BaseModel, EmailStr

class Budget(BaseModel):
    id: int
    limit_amount: float
    start_date: str
    end_date: str

class Transaction(BaseModel):
    id: int
    category_id: int
    amount: float
    date: str
    description: Optional[str] = ""

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    password_hash: str
    status: str = "active"
    created_at: str
    budget: Budget
    transactions: List[Transaction] = []