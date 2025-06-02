from pydantic import BaseModel

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    tag_id: int

    class Config:
        from_attributes = True

class TransactionTagBase(BaseModel):
    transaction_id: int
    tag_id: int
    context: str | None = None

class TransactionTagCreate(BaseModel):
    # tag_id: int
    context: str | None = None

class TransactionTagOut(TransactionTagBase):
    class Config:
        from_attributes = True

class TagUpdate(BaseModel):
    name: str | None = None