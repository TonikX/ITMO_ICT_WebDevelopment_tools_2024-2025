from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from db import get_session
from models import User as UserModel
from schemas.user import User as UserSchema, UserCreate, UserUpdate
from security.token_service import get_current_user, verify_password, get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/users/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(request: PasswordChangeRequest,
                    session: Session = Depends(get_session),
                    current_user: UserModel = Depends(get_current_user)):
    if not verify_password(request.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.password = get_password_hash(request.new_password)
    session.add(current_user)
    session.commit()


@router.post("/users/", response_model=UserSchema)
def create_user(
        user: UserCreate, session: Session = Depends(get_session)
) -> UserSchema:
    db_user = UserModel(**user.dict())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserSchema.from_orm(db_user)


@router.get("/users/{user_id}", response_model=UserSchema)
def read_user(
        user_id: int, session: Session = Depends(get_session)
) -> UserSchema:
    db_user = session.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSchema.from_orm(db_user)


@router.get("/users/", response_model=List[UserSchema])
def read_users(
        skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
) -> List[UserSchema]:
    db_users = session.query(UserModel).offset(skip).limit(limit).all()
    return [UserSchema.from_orm(user) for user in db_users]


@router.patch("/users/{user_id}", response_model=UserSchema)
def update_user(
        user_id: int, user: UserUpdate, session: Session = Depends(get_session)
) -> UserSchema:
    db_user = session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserSchema.from_orm(db_user)


@router.delete("/users/{user_id}", response_model=UserSchema)
def delete_user(
        user_id: int, session: Session = Depends(get_session)
) -> UserSchema:
    db_user = session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    response = UserSchema.from_orm(db_user)
    session.delete(db_user)
    session.commit()
    return response
