from fastapi import FastAPI, Depends, APIRouter
from models.user import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
from services.UserService import *
from schemas.user_schema import UserCreate, UserRead
from schemas.token_schema import Token

from services.AuthService import *


userRouter = APIRouter(
    prefix="/users", tags=['Users']
)

@userRouter.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@userRouter.get("/user_list", response_model=List[UserRead])
def users_list(session=Depends(get_session)) -> List[User]:
    return list_all_users(session)


@userRouter.get("/{user_id}", response_model=UserRead)
def users_get(user_id: int, session=Depends(get_session)) -> User:
    return get_user_by_id(user_id, session)


@userRouter.post("/")
def user_create(user: User, session=Depends(get_session)) -> TypedDict('Response', { "status": int, "data": User }):
    data = new_user_create(user, session)
    return {"status": 200, "data": user}


@userRouter.patch("/me/change_password")
def password_update(old_password: str,
                new_password: str,
                current_user: User = Depends(get_current_user), 
                session=Depends(get_session)
                ) -> User:
    current_user = change_password(old_password, new_password, current_user, session)
    return current_user

@userRouter.delete("/delete{user_id}")
def user_delete(user_id: int, session=Depends(get_session)):
    return delete_user(user_id, session)
    
    
@userRouter.patch("/{user_id}")
def user_update(user_id: int, user: User, session=Depends(get_session)) -> User:
    db_user = patch_user(user_id, user, session)
    return db_user