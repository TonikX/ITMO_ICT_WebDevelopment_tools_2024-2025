from typing import Optional
from .default_models import ProfileDefault, BookDefault, ShareRequestDefault, BookInfoDefault, TagDefault
from sqlmodel import SQLModel
from datetime import date

class ProfilePublic(ProfileDefault):
    id: int
    books: Optional[list[BookDefault]] = []
    sent_requests: Optional[list[ShareRequestDefault]] = []
    received_requests: Optional[list[ShareRequestDefault]] = []


class ProfilePatch(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    description: Optional[str] = None
    register_date: Optional[date] = None
    birth_date: Optional[date] = None


class BookPatch(SQLModel):
    owner_id: Optional[int] = None
    own_since: Optional[date] = None


class ShareRequestPatch(SQLModel):
    status: str


class BookPublic(BookDefault):
    id: int
    owner: ProfileDefault | None = None


class BookInfoPublic(BookInfoDefault):
    id: int
    instances: Optional[list[BookDefault]] = []
    tags: Optional[list[TagDefault]] = []


class TagPublic(TagDefault):
    id: int
    books: Optional[list[BookInfoDefault]] = []
