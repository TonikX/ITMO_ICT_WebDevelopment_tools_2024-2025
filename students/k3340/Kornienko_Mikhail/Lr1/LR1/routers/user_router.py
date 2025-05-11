from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List

from util.auth import (
    get_password_hash,
    check_password,
    generate_token,
    authenticate_user,
    TOKEN_EXPIRY
)
from connection import get_session
from models.user_model import (
    User,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdatePassword,
    UserSigninResponse
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserSigninResponse)
def signup(user_data: UserCreate, db=Depends(get_session)):
    existing = db.exec(select(User).where(User.username == user_data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd,
        email=user_data.email,
        contact_number=user_data.contact_number,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserSigninResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        contact_number=new_user.contact_number,
        access_token= generate_token({"sub": str(new_user.id)}, timedelta(minutes=TOKEN_EXPIRY))
    )


@router.post("/signin", response_model=UserSigninResponse)
def signin(user_data: UserLogin, db=Depends(get_session)):
    user = db.exec(select(User).where(User.username == user_data.username)).first()
    if not user or not check_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong credentials")

    token_expiry = timedelta(minutes=TOKEN_EXPIRY)
    token = generate_token({"sub": str(user.id)}, token_expiry)
    return UserSigninResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        contact_number=user.contact_number,
        access_token= token
    )


@router.get("/me", response_model=UserRead)
def get_profile(user: User = Depends(authenticate_user)):
    return user


@router.get("/", response_model=List[UserRead])
def get_all_users(db=Depends(get_session)):
    return db.exec(select(User)).all()


@router.patch("/change_password")
def change_password(
        pwd_update: UserUpdatePassword,
        user: User = Depends(authenticate_user),
        db=Depends(get_session),
):
    if not check_password(pwd_update.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    user.hashed_password = get_password_hash(pwd_update.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "Password changed successfully"}
