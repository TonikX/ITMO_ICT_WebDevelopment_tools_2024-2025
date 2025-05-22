from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models import User, Submission
from app.schemas.submission import SubmissionCreate, SubmissionSchema
from app.services.submission import SubmissionService

task_submission_router = APIRouter(tags=["task submissions"])
event_attached_router = APIRouter(tags=["event submissions"])
router = APIRouter(tags=["submissions"])

submission_service = SubmissionService()


@task_submission_router.post("/{task_id}/submissions", response_model=Submission)
async def create_submission(
        task_id: int,
        submission: SubmissionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> SubmissionSchema:
    return await submission_service.create_submission(db, task_id, current_user, submission)


@router.get("/submissions/mine", response_model=List[SubmissionSchema])
async def get_my_submissions(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> List[SubmissionSchema]:
    return await submission_service.get_user_submissions(db, current_user.id)


@router.get("/submissions/{team_id}", response_model=List[SubmissionSchema])
async def get_team_submissions(
        team_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> List[SubmissionSchema]:
    return await submission_service.get_team_submissions(db, team_id)


@event_attached_router.get("/{event_id}/submissions", response_model=List[SubmissionSchema])
async def get_all_submissions(
        event_id: int,
        db: AsyncSession = Depends(get_db),
) -> List[SubmissionSchema]:
    return await submission_service.get_event_submissions(db, event_id)
