from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from config import settings
from db import get_session
from schemas.user import TokenData
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def fetch_current_user(
        access_token: str = Depends(oauth2_scheme),
        db_session: Session = Depends(get_session)
) -> User:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


    try:
        decoded_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_name: str = decoded_payload.get("sub")
        if not user_name:
            raise auth_error
        token_info = TokenData(username=user_name)
    except JWTError:
        raise auth_error

    found_user = db_session.exec(User.select().where(User.username == token_info.username)).first()
    if found_user is None:
        raise auth_error


    return found_user
