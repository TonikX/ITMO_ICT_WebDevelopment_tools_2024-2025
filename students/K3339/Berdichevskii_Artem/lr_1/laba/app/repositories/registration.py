from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Registration, User
from app.repositories.base import BaseRepository
from app.schemas.registration import RegistrationCreate, RegistrationUpdate


class RegistrationRepository(BaseRepository[Registration, RegistrationCreate, RegistrationUpdate]):
    async def get_by_user_id(
            self,
            db: AsyncSession,
            user_id: int
    ):
        query = select(Registration).filter(Registration.user_id == user_id)
        res = await db.execute(query)

        return res.scalars().all()

    async def get_by_team_id(
            self,
            db: AsyncSession,
            team_id: int
    ):
        query = select(Registration).filter(Registration.team_id == team_id)
        res = await db.execute(query)

        return res.scalars().all()

    async def get_by_event_id(
            self,
            db: AsyncSession,
            event_id: int
    ):
        query = select(Registration).filter(Registration.event_id == event_id)
        res = await db.execute(query)

        return res.scalars().all()

    async def get_by_user_and_team_id(
            self,
            db: AsyncSession,
            team_id: int,
            user: User
    ):
        query = select(Registration) \
            .filter(Registration.team_id == team_id) \
            .filter(Registration.user_id == user.id)
        res = await db.execute(query)

        return res.scalars().first()


registration_repository = RegistrationRepository(Registration)
