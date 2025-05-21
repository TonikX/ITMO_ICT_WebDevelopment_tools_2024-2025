from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select
from labs.Lr1.core.auth import decode_access_token
from labs.Lr1.models import User

from labs.Lr1.connection import get_session

security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session),
):
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload["sub"]
    current_user = session.exec(select(User).where(User.id == user_id)).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    return current_user
