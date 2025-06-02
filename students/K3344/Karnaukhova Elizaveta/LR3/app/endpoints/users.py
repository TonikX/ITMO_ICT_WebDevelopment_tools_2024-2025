from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from LR1.models.User import User
from LR1.models.UserProfile import UserProfile
from .. import db
from ..auth.auth import AuthHandler
from ..auth.user_repo import find_user
from ..db import get_session
from ..schemas.user import UserCreate, UserRead, UserProfileCreate, UserProfileRead

router = APIRouter(prefix="/users", tags=["users"])

auth_handler = AuthHandler()


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_session)):
    db_user = User.from_orm(user)
    db_user.password = auth_handler.get_password_hash(user.password)  # Хэшируем пароль
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login(user: UserCreate):
    db_user = find_user(user.username)
    if not db_user or not auth_handler.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail='Invalid username or password')
    token = auth_handler.encode_token(db_user.username)
    return {"token": token}


@router.get("/me", response_model=UserRead)
def get_current_user(user: User = Depends(auth_handler.get_current_user)):
    return user


@router.get("/", response_model=List[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    users = db.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.put("/change_password")
def change_password(
        old_password: str,
        new_password: str,
        current_user: User = Depends(auth_handler.get_current_user),
        db: Session = Depends(get_session)
):
    # Проверяем старый пароль
    if not auth_handler.verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")

    # Хэшируем и сохраняем новый пароль
    current_user.password = auth_handler.get_password_hash(new_password)
    db.commit()

    return {"message": "Пароль успешно изменен"}


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User  not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User  deleted successfully"}


@router.post("/{user_id}/profile", response_model=UserProfileRead)
def create_profile(
        user_id: int, profile: UserProfileCreate, db: Session = Depends(get_session)
):
    db_profile = UserProfile.from_orm(profile, update={"user_id": user_id})
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/{user_id}/profile", response_model=UserProfileRead)
def read_profile(user_id: int, db: Session = Depends(get_session)):
    profile = db.exec(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{user_id}/profile", response_model=UserProfileRead)
def update_profile(user_id: int, profile: UserProfileCreate, db: Session = Depends(get_session)):
    db_profile = db.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db_profile.bio = profile.bio
    db_profile.experience = profile.experience
    db_profile.preferences = profile.preferences
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.delete("/{user_id}/profile", response_model=dict)
def delete_profile(user_id: int, db: Session = Depends(get_session)):
    db_profile = db.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(db_profile)
    db.commit()
    return {"detail": "Profile deleted successfully"}
