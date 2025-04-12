from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import List

from db.connection import get_session
from model.models.models import Hackathon
from model.schemas.hackathon import HackathonRead, HackathonCreate, HackathonUpdate, HackathonReadDetailed

hackathon_router = APIRouter()


@hackathon_router.get("/", response_model=List[HackathonReadDetailed])
def get_all_hackathons(session: Session = Depends(get_session)):
    return session.exec(select(Hackathon)).all()


@hackathon_router.get("/{hackathon_id}", response_model=HackathonReadDetailed)
def get_hackathon(hackathon_id: int, session: Session = Depends(get_session)):
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return hackathon


@hackathon_router.post("/", response_model=HackathonRead, status_code=201)
def create_hackathon(hackathon: HackathonCreate, session: Session = Depends(get_session)):
    new_hackathon = Hackathon.model_validate(hackathon)
    session.add(new_hackathon)
    session.commit()
    session.refresh(new_hackathon)
    return new_hackathon


@hackathon_router.patch("/{hackathon_id}", response_model=HackathonRead)
def update_hackathon(hackathon_id: int, update: HackathonUpdate, session: Session = Depends(get_session)):
    db_hackathon = session.get(Hackathon, hackathon_id)
    if not db_hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hackathon, key, value)
    session.commit()
    session.refresh(db_hackathon)
    return db_hackathon


@hackathon_router.delete("/{hackathon_id}", status_code=204)
def delete_hackathon(hackathon_id: int, session: Session = Depends(get_session)):
    db_hackathon = session.get(Hackathon, hackathon_id)
    if not db_hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    session.delete(db_hackathon)
    session.commit()
    return {"message": "Hackathon deleted"}
