from fastapi import Depends, HTTPException, APIRouter
from typing import Union
from typing_extensions import TypedDict
from sqlmodel import select
from db import get_session
from auth import auth_handler
from models import *
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()


@router.post("/login")
def user_login(user: UserAuth, session=Depends(get_session)) \
        -> TypedDict('Response', {"token": str}):
    user_found = session.exec(select(User).where(User.username == user.username)).first()
    if user_found is None:
        raise HTTPException(status_code=400, detail='Invalid username')
    verified = auth_handler.verify_password(user.password, user_found.password)
    if not verified:
        raise HTTPException(status_code=401, detail='Invalid password')
    token = auth_handler.encode_token(user_found.id)
    return {'token': token}


@router.post("/registration")
def user_registration(user: UserAuth, session=Depends(get_session)) \
        -> TypedDict('Response', {"token": str}):
    user_candidate = session.exec(select(User).where(User.username == user.username)).first()
    if user_candidate is not None:
        raise HTTPException(status_code=400, detail='Username is taken')
    user.password = auth_handler.get_password_hash(user.password)
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    token = auth_handler.encode_token(user.id)
    return {"token": token}


@router.post("/set-admin/{user_id}")
def set_user_admin(user_id: int, secretCode: str, session=Depends(get_session)):
    if secretCode != os.getenv('LAB1_ADMIN_KEY'):
        raise HTTPException(status_code=403, detail='Code is not available')
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.role = UserRole.admin
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"ok": True}


@router.post("/get-profile")
def get_profile(authUserId=Depends(auth_handler.get_user), session=Depends(get_session)) -> UserProfile:
    user = session.get(User, authUserId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/get-all")
def users_list(session=Depends(get_session)) -> List[UserPublic]:
    return session.exec(select(User)).all()


@router.get("/get-one/{user_id}")
def user_get_one(user_id: int, session=Depends(get_session)) -> UserProfile:
    return session.get(User, user_id)


@router.delete("/delete-profile")
def user_delete(authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    user = session.get(User, authUserId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.patch("/update-profile")
def user_update(
        updates: UserUpdate,
        authUserId=Depends(auth_handler.get_user),
        session=Depends(get_session)
) -> UserPublic:
    db_user = session.get(User, authUserId)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = updates.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
