from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class BaseUser(SQLModel):
    username: str = Field(..., description="Уникальное имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта пользователя")

class UserCreate(BaseUser):
    password: str = Field(..., description="Пароль")

class UserLogin(SQLModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")

class UserRead(BaseUser):
    id: int

class TokenResponse(SQLModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Тип токена (например, bearer)")

class ChangePassword(SQLModel):
    """Схема запроса для смены пароля."""
    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., description="Новый пароль")

class UserPublic(SQLModel):
    id: int | None
    username: str
    age: int | None
    info: str | None

class UserFull(UserPublic):
    email: EmailStr = Field(..., description="Электронная почта пользователя")

class UserUpdate(SQLModel):
    """Схема запроса для обновления профиля."""
    username: str | None = Field(None, description="Новое имя пользователя (уникальное)")
    age: int | None = Field(None, gt=0, description="Новый возраст (должен быть больше 0)")
    info: str | None = Field(None, description="Дополнительная информация")

