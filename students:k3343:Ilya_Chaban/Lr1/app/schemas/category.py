from sqlmodel import SQLModel
from typing import Optional


class CategoryBase(SQLModel):
    name: str
    type: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class CategoryCreate(CategoryBase):
    user_id: int


class CategoryRead(CategoryBase):
    id: int
    user: Optional[UserRead]


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[str] = None
