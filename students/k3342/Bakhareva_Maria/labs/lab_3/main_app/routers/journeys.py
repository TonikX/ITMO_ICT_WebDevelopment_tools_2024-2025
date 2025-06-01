from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session
from db.connection import get_session
from auth.utils import auth_scheme
from middleware.user import get_initiator_permission
from services.journeys_service import (
    get_journeys_with_participants,
    get_journey_with_participants,
    create_journey,
    update_journey,
    delete_journey,
)
from models.models import JourneyWithParticipants, Journey

router = APIRouter(tags=["Journeys"], prefix="/journeys")


@router.get("/", response_model=list[JourneyWithParticipants])
async def list_journeys(
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    return get_journeys_with_participants(session)


@router.get("/{journey_id}", response_model=JourneyWithParticipants)
async def get_journey_by_id(
    journey_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    journey = get_journey_with_participants(session, journey_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey


@router.post("/", response_model=Journey)
async def create_new_journey(
    journey: Journey,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    return create_journey(session, journey)


@router.put("/{journey_id}", response_model=Journey)
async def update_existing_journey(
    journey_id: int,
    journey: Journey,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    get_initiator_permission(journey_id, token=token, session=session)
    updated = update_journey(session, journey_id, journey)
    if not updated:
        raise HTTPException(status_code=404, detail="Journey not found")
    return updated


@router.delete("/{journey_id}")
async def delete_existing_journey(
    journey_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    get_initiator_permission(journey_id, token=token, session=session)
    deleted = delete_journey(session, journey_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Journey not found")
    return {"message": "Journey deleted successfully"}
