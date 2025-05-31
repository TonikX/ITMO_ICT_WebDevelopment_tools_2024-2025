from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from db.connection import get_session
from auth.utils import decode_access_token, auth_scheme
from models.models import Account


def get_current_admin(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> Account:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("scope") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    statement = select(Account).where(Account.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
