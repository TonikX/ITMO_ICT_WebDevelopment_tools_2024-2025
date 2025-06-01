from typing import Optional

from sqlmodel import SQLModel


class CategoryBase(SQLModel):
    name: str
    is_income: bool

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    is_income: Optional[bool] = None