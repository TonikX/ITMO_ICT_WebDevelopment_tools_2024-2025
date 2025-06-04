from fastapi import Depends, HTTPException
from typing_extensions import TypedDict , List
from sqlmodel import select
from app.auth import auth_handler
from app.models import User, UserAuth, UserRole, UserProfile, UserUpdate, UserPublic
from database import get_session
import os

def login(user: UserAuth, session=Depends(get_session)) -> TypedDict('Response', {"token": str}):
    user_found = session.exec(select(User).where(User.username == user.username)).first()
    if user_found is None:
        raise HTTPException(status_code=400, detail='Invalid username')
    if not auth_handler.verify_password(user.password, user_found.password):
        raise HTTPException(status_code=401, detail='Invalid password')
    return {"token": auth_handler.encode_token(user_found.id)}

def register(user: UserAuth, session=Depends(get_session)) -> TypedDict('Response', {"token": str}):
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=400, detail='Username is taken')
    user.password = auth_handler.get_password_hash(user.password)
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"token": auth_handler.encode_token(user.id)}

def set_admin(user_id: int, secretCode: str, session=Depends(get_session)):
    if secretCode != os.getenv('LAB1_ADMIN_KEY'):
        raise HTTPException(status_code=403, detail='Code is not available')
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.role = UserRole.admin
    session.add(db_user)
    session.commit()
    return {"ok": True}

def get_profile(authUserId=Depends(auth_handler.get_user), session=Depends(get_session)) -> UserProfile:
    user = session.get(User, authUserId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_all_users(session=Depends(get_session)) -> List[UserPublic]:
    return session.exec(select(User)).all()

def get_user(user_id: int, session=Depends(get_session)) -> UserProfile:
    return session.get(User, user_id)

def delete_user(authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    user = session.get(User, authUserId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

def update_user(updates: UserUpdate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)) -> UserPublic:
    db_user = session.get(User, authUserId)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
