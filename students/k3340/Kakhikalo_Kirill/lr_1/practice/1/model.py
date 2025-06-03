# Необходиом создать простой сервис для управления личными финансами. Сервис должен позволять пользователям вводить
# доходы и расходы, устанавливать бюджеты на различные категории, а также просматривать отчеты о своих финансах.
# Дополнительные функции могут включать в себя возможность получения уведомлений о превышении бюджета, анализа трат и установки целей на будущее.
from enum import Enum
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic.v1 import UUID4


class Category(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

class Budget(BaseModel):
    id: UUID
    category: List[Category] = []
    limit: int
    start_date: datetime
    end_date: datetime

class Transaction(BaseModel):
    id: UUID
    account_id: UUID
    amount: int
    timestamp: datetime
    category: Category
    description: Optional[str] = None

class Target(BaseModel):
    id: UUID
    name: str
    target_amount: int
    deadline: datetime
    created_at: datetime
    description: Optional[str] = None

class Account(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    balance: int
    currency: str
    created_at: datetime
    updated_at: datetime
    budgets: List[Budget] = []
    targets: List[Target] = []
    transactions: List[Transaction] = []

class BudgetCategory(BaseModel):
    budget_id: UUID
    category_id: UUID

class User(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    accounts: List[Account] = []
