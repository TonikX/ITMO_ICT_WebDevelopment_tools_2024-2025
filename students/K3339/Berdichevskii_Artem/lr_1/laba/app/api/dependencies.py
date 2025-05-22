from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user import user_service
from app.services.auth import get_token_data
from app.database import get_db
from app.schemas.user import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserInDB:
    token_data = await get_token_data(token)
    user = await user_service.get_by_username(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user