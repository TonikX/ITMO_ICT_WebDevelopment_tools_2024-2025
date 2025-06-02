from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.tournament_schemas import TournamentResponse, TournamentCreate, TournamentUpdate
from ..users.user_security import get_session, get_current_active_user, get_current_admin_user
from ...models import Tournament, User, Season

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("/", response_model=List[TournamentResponse])
async def list_tournaments(
        season_id: Optional[int] = None,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get list of all tournaments with optional season filter"""
    query = select(Tournament)
    if season_id:
        query = query.where(Tournament.season_id == season_id)
    result = await session.execute(query)
    tournaments = result.scalars().all()
    return tournaments


@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
        tournament: TournamentCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Create a new tournament with automatic season assignment"""
    tournament_dict = tournament.dict()

    # If season_id not provided, validate that start_date is present
    if not tournament_dict.get("season_id"):
        if not tournament.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either season_id or start_date must be provided to create a tournament"
            )

        tournament_year = tournament.start_date.year

        if tournament.start_date.month >= 7:
            season_year = f"{tournament_year}/{tournament_year + 1}"
        else:
            season_year = f"{tournament_year - 1}/{tournament_year}"

        season_result = await session.execute(
            select(Season).where(Season.year == season_year)
        )
        season = season_result.scalar_one_or_none()

        if not season:
            new_season = Season(year=season_year)
            session.add(new_season)
            await session.commit()
            await session.refresh(new_season)
            tournament_dict["season_id"] = new_season.season_id
        else:
            tournament_dict["season_id"] = season.season_id

    else:
        season_result = await session.execute(
            select(Season).where(Season.season_id == tournament_dict["season_id"])
        )
        if not season_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Season with ID {tournament_dict['season_id']} not found"
            )

    new_tournament = Tournament(**tournament_dict)
    session.add(new_tournament)
    await session.commit()
    await session.refresh(new_tournament)
    return new_tournament


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
        tournament_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Get a specific tournament by ID"""
    result = await session.execute(select(Tournament).where(Tournament.tournament_id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
        tournament_id: int,
        tournament_data: TournamentUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Update a tournament (admin only)"""
    result = await session.execute(select(Tournament).where(Tournament.tournament_id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    update_data = tournament_data.dict(exclude_unset=True)

    # If updating season_id, verify the season exists
    if "season_id" in update_data and update_data["season_id"]:
        season_result = await session.execute(
            select(Season).where(Season.season_id == update_data["season_id"])
        )
        if not season_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Season with ID {update_data['season_id']} not found"
            )

    for key, value in update_data.items():
        setattr(tournament, key, value)

    await session.commit()
    await session.refresh(tournament)
    return tournament


@router.delete("/{tournament_id}", status_code=status.HTTP_200_OK)
async def delete_tournament(
        tournament_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user),
):
    """Delete a tournament (admin only)"""
    result = await session.execute(select(Tournament).where(Tournament.tournament_id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    await session.delete(tournament)
    await session.commit()
    return {"message": f"Tournament '{tournament.name}' deleted successfully"}
