from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select

from db.connection import get_session
from auth.utils import auth_scheme
from middleware.user import get_initiator_permission
from services.participant_service import (
    get_participants,
    create_participant,
    delete_participant,
    update_participant,
)
from models.models import Participant

router = APIRouter(tags=["Participants"], prefix="/participants")


@router.get("/")
async def read_participants(
    journey_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> list[Participant]:
    participants = get_participants(session, journey_id)
    return participants


@router.post("/")
async def create_new_participant(
    participant: Participant,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Participant:
    get_initiator_permission(participant.journey_id, token=token, session=session)
    try:
        new_participant = create_participant(session, participant)
        return new_participant
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{participant_id}")
async def modify_participant(
    participant_id: int,
    participant: Participant,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Participant:
    db_participant = session.exec(select(Participant).where(Participant.id == participant_id)).one_or_none()
    if not db_participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    get_initiator_permission(db_participant.journey_id, token=token, session=session)

    try:
        updated = update_participant(session, participant_id, participant)
        if not updated:
            raise HTTPException(status_code=404, detail="Participant not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{participant_id}")
async def remove_participant(
    participant_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Participant:
    db_participant = session.exec(select(Participant).where(Participant.id == participant_id)).one_or_none()
    if not db_participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    get_initiator_permission(db_participant.journey_id, token=token, session=session)

    try:
        deleted = delete_participant(session, participant_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Participant not found")
        return deleted
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
