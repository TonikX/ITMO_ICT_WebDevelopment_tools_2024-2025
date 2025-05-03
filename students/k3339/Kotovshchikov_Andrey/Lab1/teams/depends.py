from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.depends import get_session
from teams.models import Role
from teams.services import TeamService
from users.depends import get_current_user
from users.dtos import UserDTO


def get_team_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TeamService:
    return TeamService(session)


async def check_user_is_member(
    team_id: int,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[TeamService, Depends(get_team_service)],
) -> None:
    is_member = await service.check_user_has_role(me=current_user, team_id=team_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


async def check_user_is_owner(
    team_id: int,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[TeamService, Depends(get_team_service)],
) -> None:
    is_owner = await service.check_user_has_role(
        me=current_user,
        team_id=team_id,
        role=Role.OWNER,
    )

    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
