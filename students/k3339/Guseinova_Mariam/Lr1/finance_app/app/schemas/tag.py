from pydantic import BaseModel

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    tag_id: int

    class Config:
        orm_mode = True

class TransactionTagBase(BaseModel):
    transaction_id: int
    tag_id: int
    context: str | None = None

class TransactionTagCreate(BaseModel):
    # tag_id: int
    context: str | None = None

class TransactionTagOut(TransactionTagBase):
    class Config:
        orm_mode = True

class TagUpdate(BaseModel):
    name: str | None = None