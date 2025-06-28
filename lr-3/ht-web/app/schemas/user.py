from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserAuth(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str 