from fastapi import APIRouter, HTTPException, status, Depends

from app.api.dependencies.auth import get_current_user
from app.schemas.info import MessageResponse
from app.schemas.user import UserCreate, UserLogin, UserRead, TokenResponse, ChangePassword, UserUpdate, UserFull
from app.db.session import get_session
from app.services.user_service import create_user, authenticate_user, change_user_password, get_user_by_id, update_user
from sqlmodel import Session
from app.models.models import User

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user_create: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    """
    Регистрирует нового пользователя.
    Принимает username, email и пароль, возвращает объект UserRead.
    """
    try:
        return UserRead.model_validate(create_user(user_create, session))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
def login(user_login: UserLogin, session: Session = Depends(get_session)) -> TokenResponse:
    """
    Авторизует пользователя.
    Принимает username и пароль, возвращает JWT-токен.
    """
    token = authenticate_user(user_login.username, user_login.password, session)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserFull)
def get_user_info(user_id: int = Depends(get_current_user), session: Session = Depends(get_session)) -> User:
    """
    Возвращает информацию о текущем пользователе.
    """
    return get_user_by_id(user_id, session)

@router.post("/me/change-password", response_model=MessageResponse, status_code=200)
def change_password(
    password_data: ChangePassword,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> MessageResponse:
    """Смена пароля пользователя."""
    change_user_password(user_id, password_data, session)
    return MessageResponse(message="Password changed successfully")

@router.patch("/me", response_model=UserFull)
def update_profile(
    user_update: UserUpdate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> User:
    """Обновляет профиль пользователя (username, age, info)."""
    return update_user(user_id, user_update, session)
