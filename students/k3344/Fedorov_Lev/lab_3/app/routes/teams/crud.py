import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.teams_schemas import TeamResponse, TeamAdminUpdate
from ...config import TEAM_LOGOS_DIR, save_upload_file, ALLOWED_IMAGE_TYPES
from ...models import Team, SportSchool, User, Role, UsersRoles
from ..users.user_security import get_current_active_user, get_current_admin_user, get_session

router = APIRouter(prefix="/team", tags=["teams"])


@router.get("/", response_model=List[TeamResponse])
async def list_teams(
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get list of all teams"""
    query = select(Team)
    result = await session.execute(query)
    teams = result.scalars().all()
    return teams


@router.get("/my", response_model=List[TeamResponse])
async def list_my_teams(
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get list of teams owned by the current user"""
    query = select(Team).where(Team.user_id == current_user.user_id)
    result = await session.execute(query)
    teams = result.scalars().all()
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
        team_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get a specific team by ID"""
    result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )
    return team


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
        name: str = Form(...),
        coach: Optional[str] = Form(None),
        country: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        additional_info: Optional[str] = Form(None),
        school_id: Optional[int] = Form(None),
        photo: Optional[UploadFile] = File(None),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Create a new team with optional logo upload"""
    # Check for duplicate team
    query = select(Team).where(Team.name == name)
    result = await session.execute(query)
    existing_team = result.scalar_one_or_none()

    if existing_team:
        # If team with same name exists, check country and city
        if existing_team.country == country and existing_team.city == city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team with the same name, country, and city already exists"
            )

    if school_id:
        school_result = await session.execute(
            select(SportSchool).where(SportSchool.school_id == school_id)
        )
        if not school_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport school with ID {school_id} not found"
            )

    team_data = {
        "name": name,
        "coach": coach,
        "country": country,
        "city": city,
        "additional_info": additional_info,
        "school_id": school_id,
        "user_id": current_user.user_id
    }

    photo_url = None
    if photo:
        photo_path = await save_upload_file(
            file=photo,
            directory=str(TEAM_LOGOS_DIR),
            allowed_types=ALLOWED_IMAGE_TYPES
        )
        photo_url = f"/team_logos/{os.path.basename(photo_path)}"
        team_data["photo_url"] = photo_url

    new_team = Team(**team_data)
    session.add(new_team)
    await session.commit()
    await session.refresh(new_team)
    return new_team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
        team_id: int,
        name: Optional[str] = Form(None),
        coach: Optional[str] = Form(None),
        country: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        additional_info: Optional[str] = Form(None),
        school_id: Optional[int] = Form(None),
        photo: Optional[UploadFile] = File(None),
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Update a team with optional logo upload or replacement"""
    result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )

    is_admin = any(role.role_name == "admin" for role in current_user.roles)
    if team.user_id != current_user.user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this team"
        )

    if name is not None and name != team.name:
        query = select(Team).where(Team.name == name, Team.team_id != team_id)
        result = await session.execute(query)
        existing_team = result.scalar_one_or_none()

        if existing_team:
            check_country = country if country is not None else team.country
            check_city = city if city is not None else team.city

            if existing_team.country == check_country and existing_team.city == check_city:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team with the same name, country, and city already exists"
                )

    if school_id and school_id != team.school_id:
        school_result = await session.execute(
            select(SportSchool).where(SportSchool.school_id == school_id)
        )
        if not school_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport school with ID {school_id} not found"
            )

    if name is not None:
        team.name = name
    if coach is not None:
        team.coach = coach
    if country is not None:
        team.country = country
    if city is not None:
        team.city = city
    if additional_info is not None:
        team.additional_info = additional_info
    if school_id is not None:
        team.school_id = school_id

    if photo:
        if team.photo_url:
            old_photo_path = os.path.join(TEAM_LOGOS_DIR, os.path.basename(team.photo_url))
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)

        photo_path = await save_upload_file(
            file=photo,
            directory=str(TEAM_LOGOS_DIR),
            allowed_types=ALLOWED_IMAGE_TYPES
        )

        team.photo_url = f"/team_logos/{os.path.basename(photo_path)}"

    await session.commit()
    await session.refresh(team)
    return team


@router.put("/{team_id}/admin", response_model=TeamResponse)
async def assign_team_admin(
        team_id: int,
        admin_data: TeamAdminUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )

    user_roles_query = select(Role).join(UsersRoles).where(UsersRoles.user_id == current_user.user_id)
    user_roles_result = await session.execute(user_roles_query)
    user_roles = user_roles_result.scalars().all()
    is_system_admin = any(role.role_name == "admin" for role in user_roles)

    if team.user_id != current_user.user_id and not is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this team's admin"
        )

    new_admin_result = await session.execute(
        select(User).where(User.user_id == admin_data.user_id)
    )
    new_admin = new_admin_result.scalar_one_or_none()
    if not new_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {admin_data.user_id} not found"
        )

    team.user_id = admin_data.user_id

    await session.commit()
    await session.refresh(team)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_200_OK)
async def delete_team(
        team_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Delete a team (admin or team owner only)"""
    result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )

    is_admin = any(role.role_name == "admin" for role in current_user.roles)

    if not is_admin and team.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this team"
        )

    if team.photo_url:
        logo_path = os.path.join(TEAM_LOGOS_DIR, os.path.basename(team.photo_url))
        if os.path.exists(logo_path):
            os.remove(logo_path)

    await session.delete(team)
    await session.commit()
    return {"message": f"Team {team.name} deleted successfully"}


@router.delete("/{team_id}/logo", status_code=status.HTTP_200_OK)
async def delete_team_logo(
        team_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Delete team logo"""
    result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )

    is_admin = any(role.role_name == "admin" for role in current_user.roles)
    if team.user_id != current_user.user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this team's logo"
        )

    if not team.photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This team doesn't have a logo"
        )

    logo_path = os.path.join(TEAM_LOGOS_DIR, os.path.basename(team.photo_url))
    if os.path.exists(logo_path):
        os.remove(logo_path)

    team.photo_url = None
    await session.commit()
    await session.refresh(team)

    return {"message": "Team logo deleted successfully"}
