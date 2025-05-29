from fastapi import Depends, HTTPException, APIRouter
from typing import Union
from typing_extensions import TypedDict
from sqlmodel import select
from auth import auth_handler
from db import get_session
from models import *

router = APIRouter()


@router.get("/get-all")
def hackathons_list(session=Depends(get_session)) -> List[Hackathon]:
    return session.exec(select(Hackathon)).all()


@router.get("/get-one/{hackathon_id}")
def hackathon_get_one(hackathon_id: int, session=Depends(get_session)) -> HackathonFull:
    return session.get(Hackathon, hackathon_id)


@router.post("/create")
def hackathon_create(hackathon: HackathonCreate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)) \
        -> HackathonFull:
    auth_user = session.get(User, authUserId)
    if not auth_user or auth_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")
    hackathon = Hackathon.model_validate(hackathon)
    session.add(hackathon)
    session.commit()
    session.refresh(hackathon)
    return hackathon


@router.patch("/update/{hackathon_id}")
def hackathon_update(
        hackathon_id: int,
        updates: HackathonUpdate,
        authUserId=Depends(auth_handler.get_user),
        session=Depends(get_session)
) -> HackathonFull:
    auth_user = session.get(User, authUserId)
    if not auth_user or auth_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    hackathon_data = updates.model_dump(exclude_unset=True)
    for key, value in hackathon_data.items():
        setattr(hackathon, key, value)
    session.add(hackathon)
    session.commit()
    session.refresh(hackathon)
    return hackathon


@router.delete("/delete-hackathon/{hackathon_id}")
def hackathon_delete(hackathon_id: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    auth_user = session.get(User, authUserId)
    if not auth_user or auth_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="User not available")
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    session.delete(hackathon)
    session.commit()
    return {"ok": True}
