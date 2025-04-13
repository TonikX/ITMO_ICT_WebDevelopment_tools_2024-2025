from pydantic import BaseModel
from datetime import date
from app.schemas.tag import TagOut

class TransactionBase(BaseModel):
    category_id: int
    amount: float
    description: str | None = None
    transaction_date: date

class TransactionCreate(TransactionBase):
    pass

class TransactionTagOut(BaseModel):
    tag: TagOut
    context: str | None = None

    class Config:
        orm_mode = True

class TransactionOut(TransactionBase):
    transaction_id: int
    user_id: int
    tags: list[TransactionTagOut] = [] # Добавляем список тегов

    class Config:
        orm_mode = True

class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = None
    description: str | None = None
    transaction_date: date | None = None