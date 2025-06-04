from fastapi import Depends, APIRouter
from app.controolers import submission_controller
from app.auth import auth_handler
from database import get_session
from app.models import *

router = APIRouter(prefix="/submissions", tags=["Submissions"])

@router.get("/get-all", response_model=list[Submission])
def get_all(session=Depends(get_session)):
    return submission_controller.get_all_submissions(session)

@router.get("/get-one/{submission_id}", response_model=SubmissionFull)
def get_one(submission_id: int, session=Depends(get_session)):
    return submission_controller.get_submission_by_id(submission_id, session)

@router.post("/create", response_model=SubmissionFull)
def create(submission_data: SubmissionCreate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return submission_controller.create_submission(submission_data, authUserId, session)

@router.delete("/delete-submission/{submission_id}")
def delete(submission_id: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return submission_controller.delete_submission(submission_id, authUserId, session)

@router.patch("/evaluate/{submission_id}", response_model=SubmissionFull)
def evaluate(submission_id: int, evaluation: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return submission_controller.evaluate_submission(submission_id, evaluation, authUserId, session)
