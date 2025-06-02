from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    fullname: str
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    fullname: str
    created_at: datetime

    class Config:
        orm_mode = True
