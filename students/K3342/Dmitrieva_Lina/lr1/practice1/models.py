from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

# Перечисление возможных валют
class Currency(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"

# Модель транзакции
class Transaction(BaseModel):
    id: int
    amount: float
    transaction_type: str  # "income" или "expense"
    date: str

# Модель пользователя
class User(BaseModel):
    id: int
    name: str
    email: str
    currency: Currency
    transactions: Optional[List[Transaction]] = []