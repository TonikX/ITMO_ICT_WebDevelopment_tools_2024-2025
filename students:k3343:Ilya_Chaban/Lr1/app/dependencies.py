from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.connection import get_session
from app.service.auth import decode_access_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Security(oauth2_scheme), session: Session = Depends(get_session)) -> User:

    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == token_data.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
