from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.api.v1.endpoints.registrations import team_router
from app.database import get_db
from app.repositories.team import team_repository
from app.schemas.team import TeamCreate, TeamInDB
from app.schemas.user import UserInDB
from app.services.event import event_service
from app.services.team import team_service

event_attached_router = APIRouter(prefix='/{event_id}/teams', tags=['teams'])


@event_attached_router.get('/', response_model=List[TeamInDB])
async def get_event_teams(
        event_id: int,
        db: AsyncSession = Depends(get_db),
):
    event = await event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    result = await team_service.get_event_teams(db, event.id)
    return result


@event_attached_router.post('/', response_model=TeamInDB)
async def register_team(
        event_id: int,
        team_data: TeamCreate,
        db: AsyncSession = Depends(get_db),
):
    event = await event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    result = await team_service.create_team(db, team_data, event)
    return result


router = APIRouter(prefix='/teams', tags=['teams'])
router.include_router(team_router)


@router.get('/', response_model=List[TeamInDB])
async def get_teams(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
):
    return await team_repository.get_all(db, skip=skip, limit=limit)


@router.get('/my/', response_model=List[TeamInDB])
async def get_my_teams(db: AsyncSession = Depends(get_db),
                       current_user: UserInDB = Depends(get_current_active_user), ):
    return await team_repository.get_user_teams(db, current_user)


@router.get('/{team_id}', response_model=TeamInDB)
async def get_team(
        team_id: int,
        db: AsyncSession = Depends(get_db),
):
    return await team_repository.get(db, team_id)
