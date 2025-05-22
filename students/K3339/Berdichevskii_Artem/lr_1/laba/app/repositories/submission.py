from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Team, Registration
from app.models.submission import Submission
from app.repositories.base import BaseRepository
from app.schemas.submission import SubmissionCreate


class SubmissionRepository(BaseRepository[Submission, SubmissionCreate, SubmissionCreate]):
    async def get_by_team(self, db: AsyncSession, team_id: int):
        result = await db.execute(
            select(self.model).filter(self.model.team_id == team_id)
        )
        return result.scalars().all()

    async def get_by_user(self, db: AsyncSession, user_id: int):
        result = await db.execute(
            select(self.model)
            .join(Team)
            .join(Registration, Registration.team_id == Team.id)
            .filter(Registration.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_event(self, db: AsyncSession, event_id: int):
        result = await db.execute(
            select(self.model)
            .join(Team)
            .filter(Team.event_id == event_id)
        )
        return result.scalars().all()


submission_repository = SubmissionRepository(Submission)
