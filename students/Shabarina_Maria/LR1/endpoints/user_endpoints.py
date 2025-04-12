from pydantic import BaseModel
from auth.auth import AuthHandler
from repos.user_repos import create_user, find_user, update_user
from fastapi import Depends, HTTPException, APIRouter
from models.models import *


user_router = APIRouter()
auth_handler = AuthHandler()


class UserCreate(BaseModel):
    name: str
    date_of_birth: date
    about: Optional[str] = ""
    phone_number: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(SQLModel):
    name: str
    date_of_birth: date
    about: Optional[str] = ""
    phone_number: str
    email: str


@user_router.post("/user_registration", tags=['User'], description='Регистрация пользователя')
def register(user_data: UserCreate):
    existing_user = find_user(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с такой почтой уже существует")
    hashed_password = auth_handler.hash_password(user_data.password)
    user_data.password = hashed_password
    user = create_user(user_data)
    return {"status": 200, "data": user}


@user_router.post("/user_ogin", tags=['User'], description='Вход')
def login(user_data: UserLogin):
    user = find_user(user_data.email)
    if not user or not auth_handler.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Неверные данные для входа")
    token = auth_handler.encode_token(user.email)
    return {"token": token}


@user_router.get('/user_me', tags=['User'], description='Мои данные')
def get_current_user(user: User = Depends(auth_handler.get_authenticated_user)):
    return user


@user_router.patch("/user/patch/{user_id}", tags=['User'], description='Редактирование пользователя')
def user_update(user_id: int, user_data: UserUpdate = Depends(auth_handler.get_authenticated_user)):
    updated_fields = user_data.model_dump(exclude_unset=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    user = update_user(user_id, updated_fields)
    return {"status": 200, "data": user}
