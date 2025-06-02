from fastapi import FastAPI, Depends, APIRouter, HTTPException

from models.user import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict

from services.AuthService import get_current_user, get_password_hash, verify_password

def new_user_create(user: User, session) -> User:
    hashed_password = get_password_hash(user.hash_password)
    user = User(
        email=user.email,
        fullname=user.fullname,
        hash_password=hashed_password 
    )    
    session.add(user) 
    session.commit()
    session.refresh(user)
    return user


def list_all_users(session) -> List[User]:
    return session.exec(select(User)).all()


def get_user_by_id(user_id: int, session) -> User:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")    
    return user

def change_password(old_password: str,
                new_password: str,
                current_user: User, 
                session
                ) -> User:
    if verify_password(old_password, current_user.hash_password):
        setattr(current_user, "hash_password", get_password_hash(new_password))
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

def delete_user(user_id: int, session):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}    

def patch_user(user_id: int, user: User, session) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user