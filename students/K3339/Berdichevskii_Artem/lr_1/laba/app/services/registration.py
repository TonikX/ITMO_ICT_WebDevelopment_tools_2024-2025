from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, Registration
from app.repositories.event import event_repository
from app.repositories.registration import registration_repository
from app.repositories.team import team_repository
from app.schemas.registration import RegistrationCreate


class RegistrationService:
    async def get_by_user_id(
            self,
            db: AsyncSession,
            user_id: int
    ):
        return await registration_repository.get_by_user_id(db, user_id)

    async def get_by_team_id(
            self,
            db: AsyncSession,
            team_id: int
    ):
        return await registration_repository.get_by_user_id(db, team_id)

    async def get_by_event_id(
            self,
            db: AsyncSession,
            event_id: int
    ):
        return await registration_repository.get_by_user_id(db, event_id)

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        return await registration_repository.get_all(db, skip, limit)

    async def create(
            self,
            db: AsyncSession,
            model_data: RegistrationCreate,
            user: User,
            team_id: int
    ):
        team = await team_repository.get(db, team_id)
        event = await event_repository.get(db, team.event_id)

        if not all([event, team, user]):
            raise HTTPException(404, f"data not found: {[event, team, user]}")

        model_dump = model_data.model_dump()

        model_dump['event_id'] = event.id

        model_dump['user_id'] = user.id

        model_dump['team_id'] = team.id

        return await registration_repository.create(db, Registration(**model_dump))

    async def delete_by_team_id(
            self,
            db: AsyncSession,
            team_id: int,
            user: User
    ):
        obj = await registration_repository.get_by_user_and_team_id(db, team_id, user)

        if not obj:
            raise HTTPException(404, "not found")

        return await registration_repository.delete(db, obj.id)


registration_service = RegistrationService()
