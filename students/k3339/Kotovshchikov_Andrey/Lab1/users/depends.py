from typing import Annotated

from fastapi import Depends, HTTPException, Header, status
from core.depends import get_session
from users.dtos import UserDTO
from users.services import UserService
from sqlalchemy.ext.asyncio import AsyncSession


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)


async def get_current_user(
    service: Annotated[UserService, Depends(get_user_service)],
    authorization: str = Header(default=None),
) -> UserDTO:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    authorization = authorization.strip()
    if not authorization.startswith("Bearer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication method",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await service.authenticate(token)
