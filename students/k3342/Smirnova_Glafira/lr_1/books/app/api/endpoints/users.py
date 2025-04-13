from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_session
from app.api.dependencies.auth import get_current_user
from app.models import User
from app.schemas.user import UserPublic
from app.services.user_service import get_all_users, get_user_by_id

router = APIRouter()

@router.get("/", response_model=list[UserPublic])
def list_users(
    username: str | None = Query(default=None, description="Поиск по началу username"),
    session: Session = Depends(get_session),
    _=Depends(get_current_user)
) -> list[User]:
    """
    Возвращает список всех пользователей (опционально фильтрует по username).
    """
    users = get_all_users(session, username)
    return users

@router.get("/{user_id}", response_model=UserPublic)
def retrieve_user(
    user_id: int,
    session: Session = Depends(get_session),
    _=Depends(get_current_user)
) -> User:
    """
    Возвращает одного пользователя по ID.
    """
    user = get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
