from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    """User model for response_model"""
    user_id: int
    username: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: str
    phone: Optional[str] = None


class UserPasswordPatch(BaseModel):
    password: str
    password_confirm: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    photo_url: Optional[str] = None
