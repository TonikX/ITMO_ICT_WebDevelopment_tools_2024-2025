from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.application_schemas import ApplicationResponse, ApplicationCreate, ApplicationUpdate
from ..users.user_security import get_current_admin_user, get_current_active_user, get_session
from ...models import TournamentApplication, User, Team, Tournament

router = APIRouter(prefix="/applications", tags=["tournament applications"])


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
        tournament_id: Optional[int] = None,
        team_id: Optional[int] = None,
        status: Optional[str] = None,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get list of tournament applications with optional filtering"""
    query = select(TournamentApplication)

    # фильтрация
    filters = []
    if tournament_id:
        filters.append(TournamentApplication.tournament_id == tournament_id)
    if team_id:
        filters.append(TournamentApplication.team_id == team_id)
    if status:
        filters.append(TournamentApplication.status == status)

    if filters:
        query = query.where(and_(*filters))

    result = await session.execute(query)
    applications = result.scalars().all()
    return applications


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
        application: ApplicationCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    tournament_result = await session.execute(
        select(Tournament).where(Tournament.tournament_id == application.tournament_id)
    )
    tournament = tournament_result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament with ID {application.tournament_id} not found"
        )

    team_result = await session.execute(
        select(Team).where(Team.team_id == application.team_id)
    )
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {application.team_id} not found"
        )

    existing_result = await session.execute(
        select(TournamentApplication).where(
            TournamentApplication.tournament_id == application.tournament_id,
            TournamentApplication.team_id == application.team_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application for this team and tournament already exists"
        )

    new_application = TournamentApplication(**application.dict())
    session.add(new_application)
    await session.commit()
    await session.refresh(new_application)
    return new_application


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
        application_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get a specific application by ID"""
    result = await session.execute(
        select(TournamentApplication).where(TournamentApplication.application_id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    is_admin = False
    for role in current_user.roles:
        if role.role_name == "admin":
            is_admin = True
            break

    if not is_admin:
        team_result = await session.execute(
            select(Team).where(Team.team_id == application.team_id)
        )
        team = team_result.scalar_one_or_none()

        if team.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this application"
            )

    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
        application_id: int,
        application_data: ApplicationUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(
        select(TournamentApplication).where(TournamentApplication.application_id == application_id)
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    valid_statuses = ["pending", "approved", "rejected", "withdrawn"]
    if application_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    application.status = application_data.status
    if application_data.comment is not None:
        application.comment = application_data.comment

    await session.commit()
    await session.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_200_OK)
async def delete_application(
        application_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Delete an application (admin only)"""
    result = await session.execute(
        select(TournamentApplication).where(TournamentApplication.application_id == application_id)
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found"
        )

    await session.delete(application)
    await session.commit()
    return {"message": f"Application with ID {application_id} deleted successfully"}
