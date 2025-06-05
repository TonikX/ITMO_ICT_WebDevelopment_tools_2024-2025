from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.user_security_schemas import UserResponse, UserCreate, UserPasswordPatch, UserUpdate
from ...models import User, Role, UsersRoles
from .user_security import (
    AdminUser,
    AuthenticatedUser,
    get_password_hash,
    get_session
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
        session: AsyncSession = Depends(get_session),
        current_user: User = AdminUser,
):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = AdminUser,
):
    result = await session.execute(
        select(User).where(
            or_(User.username == user.username, User.email == user.email)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        name=user.name,
        surname=user.surname,
        email=user.email,
        phone=user.phone,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get("/profile", response_model=UserResponse)
async def my_profile(current_user: User = AuthenticatedUser):
    # Здесь как сделаем фронт докрутим функционал
    return current_user


@router.patch("/password", response_model=UserResponse)
async def update_password(
        patch: UserPasswordPatch,
        session: AsyncSession = Depends(get_session),
        current_user: User = AuthenticatedUser,
):
    if patch.password != patch.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароли не совпадают"
        )

    current_user.password_hash = get_password_hash(patch.password)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = AdminUser,
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.user_id == current_user.user_id:
        raise HTTPException(status_code=403, detail="Вы не можете удалить себя, напишите главному админу")

    admin_check = await session.execute(
        select(Role)
        .join(UsersRoles, UsersRoles.role_id == Role.role_id)
        .where(UsersRoles.user_id == user.user_id, Role.role_name == "admin")
    )
    if admin_check.scalar_one_or_none() is not None:
        raise HTTPException(status_code=403, detail="Нельзя удалить другого администратора")

    await session.delete(user)
    await session.commit()
    return {"ok": True, "message": "Пользователь успешно удален", "user": user.username}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = AdminUser,
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Юзер не найден")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = AdminUser,
):
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Юзер не найден")

    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return user
