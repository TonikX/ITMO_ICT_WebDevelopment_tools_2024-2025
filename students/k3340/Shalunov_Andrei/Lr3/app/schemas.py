from typing import List, Optional
from datetime import date
from pydantic import EmailStr
from sqlmodel import SQLModel


class Register(SQLModel):
    name: str
    email: EmailStr
    password: str
    description: Optional[str] = None
    birth_date: date

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    user_id: int

class ProfileRead(SQLModel):
    id: int
    name: str
    email: EmailStr
    description: Optional[str]
    register_date: date
    birth_date: date

class ProfilePatch(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    birth_date: Optional[date] = None

class PasswordChange(SQLModel):
    old_password: str
    new_password: str


class TagCreate(SQLModel):
    name: str

class TagRead(SQLModel):
    id: int
    name: str

class TagUpdate(SQLModel):
    name: Optional[str] = None


class BookInfoCreate(SQLModel):
    title: str
    author: str
    release_date: date
    publisher: Optional[str] = None
    genre: str
    tag_ids: List[int] = []

class BookInfoRead(SQLModel):
    id: int
    title: str
    author: str
    release_date: date
    publisher: Optional[str]
    genre: str
    tags: List[TagRead]

class BookInfoUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    release_date: Optional[date] = None
    publisher: Optional[str] = None
    genre: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class BookCreate(SQLModel):
    owner_id: int
    info_id: int
    print_date: Optional[date] = None
    own_since: date

class BookRead(SQLModel):
    id: int
    info: BookInfoRead
    owner: ProfileRead
    print_date: Optional[date]
    own_since: date

class BookUpdate(SQLModel):
    print_date: Optional[date] = None
    own_since: Optional[date] = None


class ShareRequestCreate(SQLModel):
    receiver_id: int
    suggested_book_id: int
    received_book_id: int

class ShareRequestRespond(SQLModel):
    approve: bool

class ShareRequestRead(SQLModel):
    id: int
    sender: ProfileRead
    receiver: ProfileRead
    suggested_book: BookRead
    received_book: BookRead
    status: str
    requested_date: date