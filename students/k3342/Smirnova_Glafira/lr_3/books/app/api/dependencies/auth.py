from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from starlette import status
from app.core.security import AuthHandler
from app.db.session import get_session
from app.services.user_service import get_user_by_id

auth_handler = AuthHandler()

def get_current_user(
    auth: HTTPAuthorizationCredentials = Security(auth_handler.security),
    session: Session = Depends(get_session)
):
    """
    Проверяет токен и возвращает пользователя.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    user_id = auth_handler.decode_token(auth.credentials)
    if not user_id:
        raise credentials_exception

    user = get_user_by_id(int(user_id), session)
    if not user:
        raise credentials_exception

    return user.id
