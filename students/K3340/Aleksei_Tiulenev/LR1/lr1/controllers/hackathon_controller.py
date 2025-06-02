# controllers/hackathon_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models.hackathon_model import Hackathon, HackathonCreate, HackathonRead
from connection import SessionLocal
from util.auth import get_current_user

router = APIRouter()
def get_session():
    with SessionLocal() as session:
        yield session


@router.post("/", response_model=HackathonRead, tags=["Hackathons"])
def create_hackathon(hackathon_create: HackathonCreate,
                     session: Session = Depends(get_session),
                     current_user = Depends(get_current_user)):
    # Здесь можно добавить проверку: только организаторы (админы) могут создавать хакатоны
    new_hackathon = Hackathon(
        event_name=hackathon_create.event_name,
        description=hackathon_create.description,
        start_date=hackathon_create.start_date,
        end_date=hackathon_create.end_date
    )
    session.add(new_hackathon)
    session.commit()
    session.refresh(new_hackathon)
    return new_hackathon

@router.get("/", response_model=list[HackathonRead], tags=["Hackathons"])
def list_hackathons(session: Session = Depends(get_session)):
    hackathons = session.exec(select(Hackathon)).all()
    return hackathons

@router.get("/{hackathon_id}", response_model=HackathonRead, tags=["Hackathons"])
def get_hackathon(hackathon_id: int, session: Session = Depends(get_session)):
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return hackathon