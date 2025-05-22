from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Team, User, Registration
from app.repositories.base import BaseRepository
from app.schemas.team import TeamUpdate, TeamCreate


class TeamRepository(BaseRepository[Team, TeamCreate, TeamUpdate]):
    async def get_event_teams(self, db: AsyncSession, event_id: int) -> List[Team]:
        result = await db.execute(select(Team).where(Team.event_id == event_id))
        return result.scalars().all()

    async def get_user_teams(self, db: AsyncSession, user: User) -> List[Team]:
        statement = (
            select(Team)
            .join(Registration)
            .where(Registration.user_id == user.id)
            .where(Registration.team_id == Team.id)
        )
        results = await db.execute(statement)
        return results.scalars().all()

    async def get_by_user_event(self, db: AsyncSession, user_id: int, event_id: int) -> Team:
        statement = (
            select(Team)
            .join(Registration)
            .where(Registration.user_id == user_id)
            .where(Registration.team_id == Team.id)
            .where(Team.event_id == event_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()


team_repository = TeamRepository(Team)
