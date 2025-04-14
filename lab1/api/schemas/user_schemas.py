from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserReadForReg(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class BookReadForPerson(BaseModel):
    id: int
    title: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime
    email: str
    books: List[BookReadForPerson] = []


class TokenData(BaseModel):
    email: Optional[str] = None


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"
