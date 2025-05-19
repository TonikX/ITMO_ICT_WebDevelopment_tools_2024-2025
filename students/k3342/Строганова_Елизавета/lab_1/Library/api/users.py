from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import User
from schemas.user import UserCreate, UserRead, UserUpdate
from security import get_password_hash
from api.dependencies import get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=UserRead)
def register_new_user(new_user: UserCreate, db: Session = Depends(get_session)):
    # Проверка, что username или email уже не заняты
    user_exists = db.exec(
        select(User).where(
            (User.username == new_user.username) |
            (User.email == new_user.email)
        )
    ).first()

    if user_exists:
        raise HTTPException(status_code=400, detail="Username or email already taken")

    secured_password = get_password_hash(new_user.password)
    user_record = User.from_orm(new_user, update={"password_hash": secured_password})

    db.add(user_record)
    db.commit()
    db.refresh(user_record)
    return user_record


@user_router.get("/", response_model=List[UserRead])
def list_all_users(
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_session),
        logged_in_user: User = Depends(get_current_user)
):
    users_list = db.exec(select(User).offset(offset).limit(limit)).all()
    return users_list


@user_router.get("/{user_pk}", response_model=UserRead)
def get_user_by_id(user_pk: int, db: Session = Depends(get_session)):
    user_obj = db.get(User, user_pk)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user_obj


@user_router.patch("/{user_pk}", response_model=UserRead)
def modify_user(
        user_pk: int,
        user_update: UserUpdate,
        db: Session = Depends(get_session),
        logged_in_user: User = Depends(get_current_user)
):
    user_in_db = db.get(User, user_pk)
    if not user_in_db:
        raise HTTPException(status_code=404, detail="User not found")

    if logged_in_user.user_id != user_pk:
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = user_update.dict(exclude_unset=True)

    # Если обновляется пароль, то хэшируем
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for attr, val in update_data.items():
        setattr(user_in_db, attr, val)

    db.add(user_in_db)
    db.commit()
    db.refresh(user_in_db)
    return user_in_db


@user_router.delete("/{user_pk}")
def remove_user(
        user_pk: int,
        db: Session = Depends(get_session),
        logged_in_user: User = Depends(get_current_user)
):
    user_to_delete = db.get(User, user_pk)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    if logged_in_user.user_id != user_pk:
        raise HTTPException(status_code=403, detail="Permission denied")

    db.delete(user_to_delete)
    db.commit()
    return {"status": "success"}
