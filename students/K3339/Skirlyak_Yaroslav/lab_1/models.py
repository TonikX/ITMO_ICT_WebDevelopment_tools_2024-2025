from sqlmodel import Field, Relationship, SQLModel
from enum import StrEnum
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Book, User  # Для аннотаций

class BookCategory(SQLModel, table=True):
    book_id: int = Field(foreign_key="book.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    books: List["Book"] = Relationship(back_populates="categories", link_model=BookCategory)

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    books: List["Book"] = Relationship(back_populates="author")

class BookCopy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    user_id: int = Field(foreign_key="user.id")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    author_id: int = Field(foreign_key="author.id")
    author: Author = Relationship(back_populates="books")
    categories: List[Category] = Relationship(back_populates="books", link_model=BookCategory)
    copies: List["BookCopy"] = Relationship(back_populates="book")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str
    owned_copies: List["BookCopy"] = Relationship(back_populates="user")
    shared_books: List["Sharing"] = Relationship(back_populates="owner", foreign_key="[Sharing.owner_id]")
    borrowed_books: List["Sharing"] = Relationship(back_populates="taking", foreign_key="[Sharing.taking_id]")

class SharingStatus(StrEnum):
    requested = "requested"
    active = "active"
    archived = "archived"

class Sharing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    taking_id: int = Field(foreign_key="user.id")
    book_copy_id: int = Field(foreign_key="bookcopy.id")
    status: SharingStatus = Field(default=SharingStatus.requested)
    owner: User = Relationship(back_populates="shared_books", foreign_key="[Sharing.owner_id]")
    taking: User = Relationship(back_populates="borrowed_books", foreign_key="[Sharing.taking_id]")
    book_copy: BookCopy = Relationship(back_populates="sharings")

# Pydantic модели (schemas)
class CategoryBase(SQLModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

class AuthorBase(SQLModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    id: int

class BookBase(SQLModel):
    name: str
    author_id: int

class BookCreate(BookBase):
    category_ids: List[int] = []

class BookRead(BookBase):
    id: int
    author: AuthorRead
    categories: List[CategoryRead]

class UserBase(SQLModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class UserLogin(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str