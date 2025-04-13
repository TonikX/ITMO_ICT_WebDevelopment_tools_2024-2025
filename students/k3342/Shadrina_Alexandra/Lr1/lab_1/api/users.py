from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import select
from typing import List
from auth.security import hash_password, verify_password, create_jwt_token
from models import User, UserCreate, UserRead, UserResponse, UserUpdatePassword, Token
from connection import get_session
from auth.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
def register_user(user: UserCreate, session=Depends(get_session)) -> UserResponse:
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_pw,
        bio=user.bio,
        date_joined=user.date_joined
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return UserResponse(status=200, data=UserRead.model_validate(new_user))


@router.post("/login", response_model=Token)
def login(
        username: str = Form(...),
        password: str = Form(...),
        session=Depends(get_session)
) -> dict:
    db_user = session.exec(select(User).where(User.username == username)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_jwt_token(db_user.username)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users_list")
def list_users(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserRead.from_orm(current_user)


@router.put("/change_password")
def change_password(user_data: UserUpdatePassword, current_user: User = Depends(get_current_user),
                    session=Depends(get_session)):
    if not verify_password(user_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect old password")

    new_hashed_pw = hash_password(user_data.new_password)
    current_user.password_hash = new_hashed_pw
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return {"status": "success", "message": "Password updated successfully"}


@router.get("/user/{user_id}")
def get_user(user_id: int, session=Depends(get_session)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/user/{user_id}")
def delete_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
