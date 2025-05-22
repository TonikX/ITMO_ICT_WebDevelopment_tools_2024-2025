from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.database import get_db
from app.models import User
from app.schemas.registration import RegistrationDisplay, RegistrationCreate
from app.services.registration import registration_service

team_router = APIRouter(prefix='/{team_id}/register')


@team_router.post('/', response_model=RegistrationDisplay)
async def register_to_team(
        team_id: int,
        registration_data: RegistrationCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    return await registration_service.create(db, registration_data, user=current_user, team_id=team_id)


@team_router.delete('/', response_model=RegistrationDisplay)
async def register_to_team(
        team_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
):
    return await registration_service.delete_by_team_id(db, user=current_user, team_id=team_id)


