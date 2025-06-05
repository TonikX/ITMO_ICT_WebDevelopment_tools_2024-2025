from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.seasons_schemas import SeasonResponse, SeasonCreate, SeasonUpdate
from ...models import Season, Tournament, User
from .crud import TournamentResponse
from ..users.user_security import get_current_admin_user, get_current_active_user, get_session

router = APIRouter(prefix="/seasons", tags=["seasons"])


@router.get("/", response_model=List[SeasonResponse])
async def list_seasons(
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get list of all seasons"""
    query = select(Season)
    result = await session.execute(query)
    seasons = result.scalars().all()
    return seasons


@router.post("/", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
async def create_season(
        season: SeasonCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Create a new season (admin only)"""
    # Check if season already exists for this year
    existing_result = await session.execute(
        select(Season).where(Season.year == season.year)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Season for year {season.year} already exists"
        )

    new_season = Season(**season.dict())
    session.add(new_season)
    await session.commit()
    await session.refresh(new_season)
    return new_season


@router.get("/{season_id}", response_model=SeasonResponse)
async def get_season(
        season_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get a specific season by ID"""
    result = await session.execute(select(Season).where(Season.season_id == season_id))
    season = result.scalar_one_or_none()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found"
        )
    return season


@router.put("/{season_id}", response_model=SeasonResponse)
async def update_season(
        season_id: int,
        season_data: SeasonUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Update a season (admin only)"""
    result = await session.execute(select(Season).where(Season.season_id == season_id))
    season = result.scalar_one_or_none()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found"
        )

    if season_data.year != season.year:
        existing = await session.execute(
            select(Season).where(Season.year == season_data.year)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Season for year {season_data.year} already exists"
            )

    season.year = season_data.year
    await session.commit()
    await session.refresh(season)
    return season


@router.delete("/{season_id}", status_code=status.HTTP_200_OK)
async def delete_season(
        season_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Delete a season (admin only)"""
    result = await session.execute(select(Season).where(Season.season_id == season_id))
    season = result.scalar_one_or_none()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found"
        )

    # Check if season has tournaments
    tournament_result = await session.execute(
        select(Tournament).where(Tournament.season_id == season_id)
    )
    if tournament_result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete season that has tournaments. Remove tournaments first."
        )

    await session.delete(season)
    await session.commit()
    return {"message": f"Season {season.year} deleted successfully"}


@router.get("/{season_id}/tournaments", response_model=List[TournamentResponse])
async def get_season_tournaments(
        season_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get all tournaments for a specific season"""
    season_result = await session.execute(
        select(Season).where(Season.season_id == season_id)
    )
    if not season_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID {season_id} not found"
        )

    result = await session.execute(
        select(Tournament).where(Tournament.season_id == season_id)
    )
    tournaments = result.scalars().all()
    return tournaments
