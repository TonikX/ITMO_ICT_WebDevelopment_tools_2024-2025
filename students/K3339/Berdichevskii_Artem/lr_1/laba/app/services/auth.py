from datetime import timedelta

from fastapi import HTTPException

from app.core.auth import create_access_token, decode_token
from app.core.config import settings
from app.schemas.user import TokenData


async def get_token_data(token: str) -> TokenData:
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenData(username=username)


async def create_user_token(username: str) -> dict:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
