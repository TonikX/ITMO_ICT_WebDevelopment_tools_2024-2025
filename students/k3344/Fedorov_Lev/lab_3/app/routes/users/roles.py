from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.roles_schemas import RoleResponse, RoleCreate, RoleAssignment, RoleUpdate
from ...models import User, Role, UsersRoles
from .user_security import get_current_admin_user, get_session
from pydantic import BaseModel

router = APIRouter(prefix="/roles", tags=["roles"])




@router.get("/", response_model=List[RoleResponse])
async def list_roles(
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(Role))
    roles = result.scalars().all()
    return roles


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
        role: RoleCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(Role).where(Role.role_name == role.role_name))
    existing_role = result.scalar_one_or_none()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role.role_name}' already exists"
        )

    new_role = Role(role_name=role.role_name)
    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)
    return new_role


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
        role_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(Role).where(Role.role_id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
        role_id: int,
        role_data: RoleUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    # Rest of the function remains the same
    result = await session.execute(select(Role).where(Role.role_id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )

    if role.role_name != role_data.role_name:
        name_check = await session.execute(
            select(Role).where(Role.role_name == role_data.role_name)
        )
        existing_role = name_check.scalar_one_or_none()
        if existing_role and existing_role.role_id != role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role name '{role_data.role_name}' already exists"
            )

    role.role_name = role_data.role_name
    await session.commit()
    await session.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
        role_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    # Rest of function remains the same
    result = await session.execute(select(Role).where(Role.role_id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )

    if role.role_name == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete the admin role"
        )

    await session.delete(role)
    await session.commit()
    return {"message": f"Role '{role.role_name}' deleted successfully"}


@router.post("/assign", status_code=status.HTTP_200_OK)
async def assign_role_to_user(
        assignment: RoleAssignment,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    user_result = await session.execute(select(User).where(User.user_id == assignment.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {assignment.user_id} not found"
        )

    role_result = await session.execute(select(Role).where(Role.role_id == assignment.role_id))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {assignment.role_id} not found"
        )

    existing = await session.execute(
        select(UsersRoles).where(
            UsersRoles.user_id == assignment.user_id,
            UsersRoles.role_id == assignment.role_id
        )
    )
    if existing.scalar_one_or_none():
        return {"message": f"Role '{role.role_name}' is already assigned to user '{user.username}'"}

    new_assignment = UsersRoles(user_id=assignment.user_id, role_id=assignment.role_id)
    session.add(new_assignment)
    await session.commit()
    return {"message": f"Role '{role.role_name}' assigned to user '{user.username}' successfully"}


@router.delete("/remove", status_code=status.HTTP_200_OK)
async def remove_role_from_user(
        assignment: RoleAssignment,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(
        select(UsersRoles).where(
            UsersRoles.user_id == assignment.user_id,
            UsersRoles.role_id == assignment.role_id
        )
    )
    user_role = result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )

    user_result = await session.execute(select(User).where(User.user_id == assignment.user_id))
    role_result = await session.execute(select(Role).where(Role.role_id == assignment.role_id))
    user = user_result.scalar_one_or_none()
    role = role_result.scalar_one_or_none()

    if role and role.role_name == "admin":
        admin_count = await session.execute(
            select(UsersRoles)
            .join(Role, UsersRoles.role_id == Role.role_id)
            .where(Role.role_name == "admin")
        )
        if len(list(admin_count.scalars().all())) <= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove the last admin role assignment"
            )

    await session.delete(user_role)
    await session.commit()
    return {
        "message": f"Role '{role.role_name if role else ''}' removed from user '{user.username if user else ''}'"
    }


@router.get("/user/{user_id}", response_model=List[RoleResponse])
async def get_user_roles(
        user_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    user_exists = await session.execute(select(User).where(User.user_id == user_id))
    if not user_exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    result = await session.execute(
        select(Role)
        .join(UsersRoles, UsersRoles.role_id == Role.role_id)
        .where(UsersRoles.user_id == user_id)
    )
    roles = result.scalars().all()
    return roles
