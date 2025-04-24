from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.utils.security import hash_password, verify_password, get_current_user

router = APIRouter()


@router.get("/users", response_model=list[User])
def get_users(session: Session = Depends(get_session), current_user: str = Depends(get_current_user)):
    """
    Получить список всех пользователей.
    Этот эндпоинт защищён JWT-токеном.
    """
    users = session.exec(select(User)).all()
    return users


@router.put("/users/change-password")
def change_password(
        old_password: str = Body(..., embed=True),
        new_password: str = Body(..., embed=True),
        session: Session = Depends(get_session),
        current_username: str = Depends(get_current_user)
):
    """
    Сменить пароль текущего пользователя.
    Требуется указать старый пароль и новый пароль.
    """
    user = session.exec(select(User).where(User.username == current_username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password")
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()
    return {"message": "Password changed successfully"}
