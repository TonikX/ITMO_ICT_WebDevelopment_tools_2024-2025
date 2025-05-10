from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth.auth import AuthHandler
from model.models.models import Participant, User, Team
from model.schemas.participant import ParticipantRead, ParticipantCreate, ParticipantJoinTeam
from db.connection import get_session

participant_router = APIRouter()
auth_handler = AuthHandler()


@participant_router.post("/", response_model=ParticipantRead, status_code=201)
def register_participant(participant: ParticipantCreate,
                         session: Session = Depends(get_session),
                         current_user: User = Depends(auth_handler.get_current_user)):
    existing = session.exec(
        select(Participant).where(
            (Participant.user_id == current_user.id) &
            (Participant.hackathon_id == participant.hackathon_id)
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    p = Participant(hackathon_id=participant.hackathon_id, user_id=current_user.id)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@participant_router.patch("/{participant_id}/approve", response_model=ParticipantRead)
def approve_participant(participant_id: int, session: Session = Depends(get_session)):
    participant = session.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    participant.is_approved = True
    session.commit()
    session.refresh(participant)
    return participant

@participant_router.post("/join-team", response_model=ParticipantRead)
def join_team(data: ParticipantJoinTeam, session: Session = Depends(get_session)):
    participant = session.get(Participant, data.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    team = session.get(Team, data.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    participant.team_id = data.team_id
    session.commit()
    session.refresh(participant)
    return participant