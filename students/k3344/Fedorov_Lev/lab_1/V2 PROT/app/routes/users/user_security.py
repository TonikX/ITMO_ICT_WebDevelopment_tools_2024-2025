from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import settings
from ...db import get_session
from ...models import User, Role, UsersRoles

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Union[User, bool]:
    user = await get_user(session, username)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


async def get_user(session: AsyncSession, username) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# Dependency functions
async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception

        user = await get_user(session, username)
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


AuthenticatedUser = Depends(get_current_active_user)


async def get_current_fresh_user(request: Request, current_user: User = Depends(get_current_user)) -> User:
    fresh = request.query_params.get("fresh", "").lower() == "true"
    if fresh:
        token = request.headers.get("Authorization", "")
        if token.startswith("Bearer "):
            token = token[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if not payload.get("fresh", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Fresh token required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return current_user


AuthenticatedFreshUser = Depends(get_current_fresh_user)


async def get_current_admin_user(current_user: User = Depends(get_current_active_user),
                                 session: AsyncSession = Depends(get_session)) -> User:
    result = await session.execute(
        select(Role)
        .join(UsersRoles, UsersRoles.role_id == Role.role_id)
        .where(UsersRoles.user_id == current_user.user_id, Role.role_name == "admin")
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


AdminUser = Depends(get_current_admin_user)


async def validate_token(token: str = Depends(oauth2_scheme),
                         session: AsyncSession = Depends(get_session)) -> User:
    return await get_current_user(token=token, session=session)
