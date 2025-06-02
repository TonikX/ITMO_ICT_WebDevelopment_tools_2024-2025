from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from api.dependency import get_current_user
from api.models.connection import get_session
from api.models.models import User
from api.schemas.user_schemas import UserCreate, UserRead, UserUpdate, Token
from core.security import get_password_hash, verify_password, create_access_token

user_router = APIRouter()
user_protected_router = APIRouter(dependencies=[Depends(get_current_user)])

@user_router.post("/register", response_model=UserRead)
def user_register(user: UserCreate, session=Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@user_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@user_protected_router.get("/users_get", response_model=List[UserRead])
def users_get(session=Depends(get_session)):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@user_protected_router.get("/user_get_{user_id}", response_model=UserRead)
def user_get(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Users not found")
    return user


@user_protected_router.patch("/user_update_{user_id}", response_model=UserRead)
def user_update(user_id: int, user_data: UserUpdate, session=Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.commit()
    session.refresh(db_user)
    return db_user


@user_protected_router.delete("/delete_{user_id}")
def delete_user(user_id: int, session=Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()
    return {"ok": True}
