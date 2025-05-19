from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    profile_info: Optional[str] = None
    skills: Optional[str] = None
    preferences: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    profile_info: Optional[str] = None
    skills: Optional[str] = None
    preferences: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
