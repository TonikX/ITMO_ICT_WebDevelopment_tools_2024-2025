from fastapi import Depends, HTTPException, APIRouter
from typing import Union
from typing_extensions import TypedDict
from sqlmodel import select
from auth import auth_handler
from db import get_session
from models import *

router = APIRouter()


@router.get("/get-all")
def submissions_list(session=Depends(get_session)) -> List[Submission]:
    return session.exec(select(Submission)).all()


@router.get("/get-one/{submission_id}")
def submission_get_one(submission_id: int, session=Depends(get_session)) -> SubmissionFull:
    return session.get(Submission, submission_id)


@router.post("/create")
def create_submission(submission_data: SubmissionCreate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)) -> SubmissionFull:
    auth_member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == submission_data.team_id, MemberTeamLink.user_id == authUserId)).first()
    if auth_member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    submission_model = Submission.model_validate(submission_data)
    session.add(submission_model)
    session.commit()
    session.refresh(submission_model)
    return submission_model


@router.delete("/delete-submission/{submission_id}")
def delete_submission(submission_id: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    auth_member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == submission.team_id, MemberTeamLink.user_id == authUserId)).first()
    if auth_member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    session.delete(submission)
    session.commit()
    return {"ok": True}


@router.patch("/evaluate/{submission_id}")
def submission_evaluate(
        evaluation: int,
        submission_id: str,
        authUserId=Depends(auth_handler.get_user),
        session=Depends(get_session)
) -> SubmissionFull:
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    auth_member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == submission.team_id, MemberTeamLink.user_id == authUserId)).first()
    if auth_member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    setattr(submission, 'evaluation', evaluation)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission

