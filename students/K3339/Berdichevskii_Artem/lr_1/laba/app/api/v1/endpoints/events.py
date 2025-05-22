import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.api.v1.endpoints.submissions import event_attached_router as submissions_router
from app.api.v1.endpoints.teams import event_attached_router as teams_router
from app.api.v1.endpoints.tasks import event_attached_router as tasks_router
from app.database import get_db
from app.schemas.event import EventList, EventInDb, EventBase
from app.schemas.user import UserInDB
from app.services.event import event_service

router = APIRouter(prefix='/events', tags=['events'])
router.include_router(teams_router)
router.include_router(tasks_router)
router.include_router(submissions_router)


@router.get(path='/', response_model=List[EventList])
async def get_events(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        from_date: Optional[datetime.date] = None,
        to_date: Optional[datetime.date] = None,
        due_register_date: Optional[datetime.date] = None
):
    return await event_service.get_events(
        db,
        skip=skip,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
        due_register_date=due_register_date
    )


@router.post(path='/', response_model=EventInDb)
async def create_event(
        event: EventBase,
        db: AsyncSession = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await event_service.create(db, event)


@router.get(path='/{id}', response_model=EventInDb)
async def get_event_by_id(
        event_id: int,
        db: AsyncSession = Depends(get_db),
):
    return await event_service.get_event_by_id(db, event_id)


@router.put(path='/{id}', response_model=EventInDb)
async def update_event(
        event_id: int,
        event: EventBase,
        db: AsyncSession = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await event_service.update_event(db, event, event_id)
