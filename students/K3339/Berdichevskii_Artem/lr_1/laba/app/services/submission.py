from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Submission
from app.repositories.submission import submission_repository
from app.repositories.task import task_repository
from app.repositories.team import team_repository
from app.schemas.submission import SubmissionCreate, SubmissionSchema


class SubmissionService:
    def __init__(self):
        self.repository = submission_repository

    async def create_submission(
            self, db: AsyncSession, task_id: int, user: User, submission: SubmissionCreate
    ) -> SubmissionSchema:
        task = await task_repository.get(db, task_id)
        if not task:
            raise HTTPException(404, "Task not found")
        if not task.event:
            raise HTTPException(404, "Task has no associated event")

        team = await team_repository.get_by_user_event(db, user.id, task.event.id)
        if not team:
            raise HTTPException(404, "User has no team for this event")

        submission_dict = submission.model_dump()
        submission_dict["team_id"] = team.id
        submission_dict["task_id"] = task_id
        return await self.repository.create(db, Submission(**submission_dict))

    async def get_team_submissions(
            self, db: AsyncSession, team_id: int
    ) -> list[SubmissionSchema]:
        return await self.repository.get_by_team(db, team_id)

    async def get_user_submissions(
            self, db: AsyncSession, user_id: int
    ) -> list[SubmissionSchema]:
        return await self.repository.get_by_user(db, user_id)

    async def get_event_submissions(
            self, db: AsyncSession, event_id: int
    ) -> list[SubmissionSchema]:
        return await self.repository.get_by_event(db, event_id)
