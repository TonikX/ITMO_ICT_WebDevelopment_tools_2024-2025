from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=128, description="Текущий пароль "
                                                                             "пользователя")
    new_password: str = Field(..., min_length=6, max_length=128, description="Новый пароль "
                                                                             "пользователя")
