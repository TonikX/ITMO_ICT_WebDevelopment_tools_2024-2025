from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from typing import List
from auth.auth import authenticate_request
from models.models import Participant, ParticipantCreate
from db import get_session

router = APIRouter(prefix="/participants", tags=["Participants"], dependencies=[Depends(authenticate_request)])


@router.get("/", response_model=List[Participant])
def get_all_participants(session: Session = Depends(get_session)):
    participants = session.exec(select(Participant).options(selectinload(Participant.user), selectinload(Participant.trip))).all()
    return participants


@router.get("/{participant_id}", response_model=Participant)
def get_participant(participant_id: int, session: Session = Depends(get_session)):
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Такого участника нет")
    return participant


@router.post("/", response_model=Participant)
def create_participant(participant_data: ParticipantCreate, session: Session = Depends(get_session)):
    participant = Participant(**participant_data.dict())
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant

@router.delete("/{participant_id}")
def delete_participant(participant_id: int, session: Session = Depends(get_session)):
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Такого участника нет")
    session.delete(participant)
    session.commit()
    return {"message": "Участник удален"}
