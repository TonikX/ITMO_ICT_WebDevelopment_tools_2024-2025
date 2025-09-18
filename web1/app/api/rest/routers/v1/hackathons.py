from fastapi import Depends, APIRouter
from app.controolers import hackathon_controller
from app.auth import auth_handler
from database import get_session
from app.models import *

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.get("/get-all", response_model=list[Hackathon])
def get_all(session=Depends(get_session)):
    return hackathon_controller.get_all_hackathons(session)


@router.get("/get-one/{hackathon_id}", response_model=HackathonFull)
def get_one(hackathon_id: int, session=Depends(get_session)):
    return hackathon_controller.get_hackathon_by_id(hackathon_id, session)


@router.post("/create", response_model=HackathonFull)
def create(hackathon: HackathonCreate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return hackathon_controller.create_hackathon(hackathon, authUserId, session)


@router.patch("/update/{hackathon_id}", response_model=HackathonFull)
def update(hackathon_id: int, updates: HackathonUpdate, authUserId=Depends(auth_handler.get_user),
           session=Depends(get_session)):
    return hackathon_controller.update_hackathon(hackathon_id, updates, authUserId, session)


@router.delete("/delete-hackathon/{hackathon_id}")
def delete(hackathon_id: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    return hackathon_controller.delete_hackathon(hackathon_id, authUserId, session)
