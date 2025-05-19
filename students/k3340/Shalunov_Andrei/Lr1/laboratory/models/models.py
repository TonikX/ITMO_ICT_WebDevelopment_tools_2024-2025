from sqlmodel import SQLModel, Field, Relationship
from .default_models import *

class Profile(ProfileDefault, table=True):
    id: int = Field(default=None, primary_key=True)

class BookInfo(BookInfoDefault, table=True):
    id: int = Field(default=None, primary_key=True)

class Book(BookDefault, table=True):
    id: int = Field(default=None, primary_key=True)
