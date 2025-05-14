# controllers/submission_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from models.submission_model import Submission, SubmissionCreate, SubmissionRead
from connection import SessionLocal
from util.auth import get_current_user

router = APIRouter()
def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/", response_model=SubmissionRead, tags=["Submissions"])
def create_submission(submission_create: SubmissionCreate,
                      session: Session = Depends(get_session),
                      current_user = Depends(get_current_user)):
    # При отправке сабмишена указывается task_id, и либо user_id, либо team_id
    new_submission = Submission(
        description=submission_create.description,
        file_url=submission_create.file_url,
        task_id=submission_create.task_id,
        user_id=current_user.id,
        team_id=submission_create.team_id  # если работа отправлена от команды, передается team_id
    )
    session.add(new_submission)
    session.commit()
    session.refresh(new_submission)
    return new_submission

@router.get("/", response_model=list[SubmissionRead], tags=["Submissions"])
def list_submissions(session: Session = Depends(get_session)):
    submissions = session.exec(select(Submission)).all()
    return submissions

@router.get("/{submission_id}", response_model=SubmissionRead, tags=["Submissions"])
def get_submission(submission_id: int, session: Session = Depends(get_session)):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission

@router.put("/{submission_id}/evaluate", response_model=SubmissionRead, tags=["Submissions"])
def evaluate_submission(submission_id: int, evaluation: float,
                        session: Session = Depends(get_session),
                        current_user = Depends(get_current_user)):
    # Обычно право оценивать имеет только организатор или админ
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    submission.evaluation = evaluation
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission