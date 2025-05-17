from pydantic import BaseModel


class TransactionCategoryBase(BaseModel):
    transaction_id: int
    category_id: int
    amount: float

class TransactionCategoryCreate(TransactionCategoryBase):
    pass

class TransactionCategoryRead(TransactionCategoryBase):
    id: int

    class Config:
        from_attributes = True