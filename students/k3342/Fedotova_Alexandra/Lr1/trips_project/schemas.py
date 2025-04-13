from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    id: int
    username: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None

    class Config:
        orm_mode = True

class TripBase(BaseModel):
    id: int
    destination: str
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None

    class Config:
        orm_mode = True 

class UserWithTrips(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int] = None
    bio: Optional[str] = None
    trips: List[TripBase]

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    id: int
    sender_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True

class TripWithMessages(BaseModel):
    id: int
    owner_id: int
    destination: str
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None
    messages: List[MessageBase]

    class Config:
        orm_mode = True