from typing import Annotated
from pydantic import AfterValidator, EmailStr
from sqlmodel import Field
from core.dtos import CoreDTO


class UserCreateDTO(CoreDTO):
    email: Annotated[EmailStr, AfterValidator(str)]
    password: Annotated[str, Field(min_length=5, max_length=100)]


class UserDTO(CoreDTO):
    id: int
    email: EmailStr


class UserTokenDTO(CoreDTO):
    token: str
    user: UserDTO


class UserChangePasswordDTO(CoreDTO):
    email: EmailStr
    new_password: str
