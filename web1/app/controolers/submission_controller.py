from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import *


def get_all_submissions(session: Session) -> list[Submission]:
    return session.exec(select(Submission)).all()


def get_submission_by_id(submission_id: int, session: Session) -> SubmissionFull:
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


def create_submission(submission_data: SubmissionCreate, user_id: int, session: Session) -> SubmissionFull:
    link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == submission_data.team_id,
        MemberTeamLink.user_id == user_id)).first()

    if not link:
        raise HTTPException(status_code=403, detail="User not available")

    submission = Submission.model_validate(submission_data)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


def delete_submission(submission_id: int, user_id: int, session: Session):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == submission.team_id,
        MemberTeamLink.user_id == user_id)).first()

    if not link:
        raise HTTPException(status_code=403, detail="User not available")

    session.delete(submission)
    session.commit()
    return {"ok": True}


def evaluate_submission(submission_id: int, evaluation: int, user_id: int, session: Session) -> SubmissionFull:
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == submission.team_id,
        MemberTeamLink.user_id == user_id)).first()

    if not link:
        raise HTTPException(status_code=403, detail="User not available")

    submission.evaluation = evaluation
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission
