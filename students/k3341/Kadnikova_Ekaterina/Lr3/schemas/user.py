from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class UserBase(SQLModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(UserBase):
    password: str

class UserLogin(SQLModel):
    username: str
    password: str