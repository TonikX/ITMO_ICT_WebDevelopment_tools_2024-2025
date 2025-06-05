from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import Player, User
from ..players.crud import (
    PlayerResponse, PlayerCreate, PlayerUpdate,
    create_player, update_player, delete_player,
    get_team, check_team_permission, transfer_player
)
from ..users.user_security import get_current_active_user, get_session

router = APIRouter(prefix="/team", tags=["team players"])

@router.get("/{team_id}/players", response_model=List[PlayerResponse])
async def list_team_players(
        team_id: int,
        session: AsyncSession = Depends(get_session),
):
    """List all players in a specific team"""
    team = await get_team(team_id, session)

    result = await session.execute(select(Player).where(Player.team_id == team_id))
    players = result.scalars().all()

    response = []
    for player in players:
        player_dict = {
            **{c.name: getattr(player, c.name) for c in Player.__table__.columns},
            "team_name": team.name
        }
        response.append(player_dict)

    return response

@router.post("/{team_id}/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def add_player_to_team(
        team_id: int,
        player_data: PlayerCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Add a player to a specific team"""
    player_with_team = PlayerCreate(**player_data.dict(), team_id=team_id)
    return await create_player(player_with_team, session, current_user)

@router.get("/{team_id}/player/{player_id}", response_model=PlayerResponse)
async def get_team_player(
        team_id: int,
        player_id: int,
        session: AsyncSession = Depends(get_session),
):
    """Get a specific player from a team"""
    team = await get_team(team_id, session)

    result = await session.execute(
        select(Player).where(
            Player.player_id == player_id,
            Player.team_id == team_id
        )
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found in team {team_id}"
        )

    response = {
        **{c.name: getattr(player, c.name) for c in Player.__table__.columns},
        "team_name": team.name
    }

    return response

@router.put("/{team_id}/player/{player_id}", response_model=PlayerResponse)
async def update_team_player(
        team_id: int,
        player_id: int,
        player_data: PlayerUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Update a player in a specific team"""
    result = await session.execute(
        select(Player).where(
            Player.player_id == player_id,
            Player.team_id == team_id
        )
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found in team {team_id}"
        )

    updated_data = PlayerUpdate(**player_data.dict(exclude_unset=True), team_id=team_id)
    return await update_player(player_id, updated_data, session, current_user)

@router.delete("/{team_id}/player/{player_id}", status_code=status.HTTP_200_OK)
async def remove_player_from_team(
        team_id: int,
        player_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Remove a player from a specific team"""
    result = await session.execute(
        select(Player).where(
            Player.player_id == player_id,
            Player.team_id == team_id
        )
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found in team {team_id}"
        )

    return await delete_player(player_id, session, current_user)

@router.post("/{team_id}/player/{player_id}/transfer", response_model=PlayerResponse)
async def transfer_player_from_team(
        team_id: int,
        player_id: int,
        new_team_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Transfer a player from current team to a new team"""
    # Check if player exists in this team
    result = await session.execute(
        select(Player).where(
            Player.player_id == player_id,
            Player.team_id == team_id
        )
    )
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found in team {team_id}"
        )

    # Check if target team is the same as current
    if team_id == new_team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer player to the same team"
        )


    return await transfer_player(player_id, new_team_id, session, current_user)