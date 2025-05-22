from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user
from app.repositories.user import user_repository
from app.schemas.user import UserInDB
from app.services.user import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserInDB])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await user_repository.get_all(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserInDB)
async def read_user_me(
        current_user: UserInDB = Depends(get_current_active_user),
):
    return current_user


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_user),
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = await user_repository.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/change-password", response_model=UserInDB)
async def change_password(
        current_password: str,
        new_password: str,
        db: AsyncSession = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_user),
):
    try:
        return await user_service.change_password(
            db, current_user, current_password, new_password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
