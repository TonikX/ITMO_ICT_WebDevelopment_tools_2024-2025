from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from app.users.service import UserService

from .model import User

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(UserService)],
) -> User:
    user: User | None = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
