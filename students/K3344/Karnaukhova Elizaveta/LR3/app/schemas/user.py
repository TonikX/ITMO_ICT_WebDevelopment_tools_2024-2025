from typing import Optional, List, ForwardRef
from pydantic import BaseModel, EmailStr, Field

# Объявляем ForwardRef для разрыва циклических зависимостей
UserBookRead = ForwardRef('UserBookRead')


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    experience: Optional[str] = None
    preferences: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: int
    user: UserRead
    books: List[UserBookRead] = Field(default_factory=list)


# Определяем UserBookRead после всех зависимостей
class UserBookRead(BaseModel):
    book_item_id: int
    status: str  # Или используйте BookStatus если нужно


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# Обновляем ForwardRef
UserProfileRead.update_forward_refs()
