from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from typing import List
from connection import get_session
from util.auth import authenticate_user
from models.submission_model import Submission, SubmissionCreate, SubmissionWithFullDetails
from models.team_model import Team
from models.task_model import Task
from models.user_model import User

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", response_model=Submission)
def create_submission(submission: SubmissionCreate, current_user: User = Depends(authenticate_user),
                      session=Depends(get_session)):
    team = session.get(Team, submission.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if current_user not in (team.members or []) and team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="User is not a member of the specified team")
    task = session.get(Task, submission.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    new_submission = Submission(**submission.dict())
    session.add(new_submission)
    session.commit()
    session.refresh(new_submission)
    return submission


@router.get("/", response_model=List[SubmissionWithFullDetails])
def list_submissions(session=Depends(get_session)):
    return session.exec(select(Submission)).all()


@router.get("/{submission_id}", response_model=SubmissionWithFullDetails)
def get_submission(submission_id: int, session=Depends(get_session)):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
