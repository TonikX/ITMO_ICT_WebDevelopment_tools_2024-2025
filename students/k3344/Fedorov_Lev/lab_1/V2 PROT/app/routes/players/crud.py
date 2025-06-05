from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from ..schemas.player_schemas import PlayerResponse, PlayerCreate, PlayerDetailResponse, PlayerUpdate
from ...models import Player, Team, User
from ..users.user_security import get_current_admin_user, get_current_active_user, get_session

from typing import Optional, List
from datetime import date




router = APIRouter(prefix="/players", tags=["players"])


async def get_user_with_roles(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.user_id == user_id).options(selectinload(User.roles))
    )
    return result.scalar_one()


async def get_team(team_id: int, session: AsyncSession):
    result = await session.execute(select(Team).where(Team.team_id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found")
    return team


async def get_player(player_id: int, session: AsyncSession):
    result = await session.execute(select(Player).where(Player.player_id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found"
        )
    return player


async def check_team_permission(team: Team, user: User, session: AsyncSession):
    user_with_roles = await get_user_with_roles(user.user_id, session)
    is_admin = any(role.role_name == "admin" for role in user_with_roles.roles)
    if not is_admin and team.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions for this team")
    return is_admin


async def check_player_permission(player: Player, user: User, session: AsyncSession):
    if player.team_id is None:
        user_with_roles = await get_user_with_roles(user.user_id, session)
        is_admin = any(role.role_name == "admin" for role in user_with_roles.roles)
        if not is_admin:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return is_admin

    team = await get_team(player.team_id, session)
    return await check_team_permission(team, user, session)


@router.get("/", response_model=List[PlayerResponse])
async def list_players(
        name: Optional[str] = None,
        team_id: Optional[int] = None,
        position: Optional[str] = None,
        country: Optional[str] = None,
        session: AsyncSession = Depends(get_session),
):
    query = select(Player)

    if name:
        query = query.where(
            or_(
                Player.first_name.ilike(f"%{name}%"),
                Player.last_name.ilike(f"%{name}%")
            )
        )
    if team_id:
        query = query.where(Player.team_id == team_id)
    if position:
        query = query.where(Player.position == position)
    if country:
        query = query.where(Player.country.ilike(f"%{country}%"))

    result = await session.execute(query)
    players = result.scalars().all()

    team_map = {}
    team_ids = [p.team_id for p in players if p.team_id is not None]
    if team_ids:
        team_query = select(Team).where(Team.team_id.in_(team_ids))
        team_result = await session.execute(team_query)
        teams = team_result.scalars().all()
        team_map = {team.team_id: team.name for team in teams}

    response = []
    for player in players:
        player_dict = {
            **{c.name: getattr(player, c.name) for c in Player.__table__.columns},
            "team_name": team_map.get(player.team_id) if player.team_id else None
        }
        response.append(player_dict)

    return response


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
        player: PlayerCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    team_name = None
    if player.team_id:
        team = await get_team(player.team_id, session)
        await check_team_permission(team, current_user, session)
        team_name = team.name
    else:
        user_with_roles = await get_user_with_roles(current_user.user_id, session)
        is_admin = any(role.role_name == "admin" for role in user_with_roles.roles)
        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Only admins can create players without a team"
            )

    player_data = player.dict()
    new_player = Player(**player_data)
    session.add(new_player)
    await session.commit()
    await session.refresh(new_player)

    response = {
        **{c.name: getattr(new_player, c.name) for c in Player.__table__.columns},
        "team_name": team_name
    }

    return response


@router.get("/{player_id}", response_model=PlayerDetailResponse)
async def get_player_details(
        player_id: int,
        session: AsyncSession = Depends(get_session),
):
    player = await get_player(player_id, session)

    team = None
    if player.team_id:
        team_result = await session.execute(
            select(Team).where(Team.team_id == player.team_id)
        )
        team = team_result.scalar_one_or_none()

    response = {
        **{c.name: getattr(player, c.name) for c in Player.__table__.columns},
        "team": team
    }

    return response


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
        player_id: int,
        player_data: PlayerUpdate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    player = await get_player(player_id, session)

    await check_player_permission(player, current_user, session)

    team_name = None
    if player_data.team_id is not None and player_data.team_id != player.team_id:
        new_team = await get_team(player_data.team_id, session)
        await check_team_permission(new_team, current_user, session)
        team_name = new_team.name
    elif player.team_id:
        team = await get_team(player.team_id, session)
        team_name = team.name

    for key, value in player_data.dict(exclude_unset=True).items():
        setattr(player, key, value)

    await session.commit()
    await session.refresh(player)

    response = {
        **{c.name: getattr(player, c.name) for c in Player.__table__.columns},
        "team_name": team_name
    }

    return response


@router.delete("/{player_id}", status_code=status.HTTP_200_OK)
async def delete_player(
        player_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Delete a player (admin or team owner)"""
    player = await get_player(player_id, session)

    await check_player_permission(player, current_user, session)

    await session.delete(player)
    await session.commit()
    return {"message": f"Player {player.first_name} {player.last_name} deleted successfully"}

@router.post("/{player_id}/transfer", response_model=PlayerResponse)
async def transfer_player(
        player_id: int,
        team_id: int,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_active_user),
):
    """Transfer a player to another team (requires permission for both teams)"""
    player = await get_player(player_id, session)

    if player.team_id == team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already in this team"
        )

    if player.team_id is not None:
        current_team = await get_team(player.team_id, session)
        await check_team_permission(current_team, current_user, session)
    else:
        user_with_roles = await get_user_with_roles(current_user.user_id, session)
        is_admin = any(role.role_name == "admin" for role in user_with_roles.roles)
        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Only admins can transfer players who don't belong to a team"
            )

    new_team = await get_team(team_id, session)
    await check_team_permission(new_team, current_user, session)

    player.team_id = team_id
    await session.commit()
    await session.refresh(player)

    response = {
        **{c.name: getattr(player, c.name) for c in Player.__table__.columns},
        "team_name": new_team.name
    }

    return response