from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from db.connection import get_session
from auth.utils import auth_scheme
from middleware.user import get_initiator_permission
from services.journey_stops_service import (
    get_journey_stops,
    add_journey_stop,
    delete_journey_stop,
)
from models.models import JourneyStop

router = APIRouter(tags=["Journey Stops"], prefix="/journey-stops")


@router.get("/{journey_id}", response_model=list[JourneyStop])
async def read_journey_stops(
    journey_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> list[JourneyStop]:
    return get_journey_stops(session, journey_id)


@router.post("/", response_model=JourneyStop)
async def create_journey_stop(
    stop: JourneyStop,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> JourneyStop:
    get_initiator_permission(stop.journey_id, token=token, session=session)
    try:
        return add_journey_stop(session, stop)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{journey_id}/{stop_id}", response_model=bool)
async def remove_journey_stop(
    journey_id: int,
    stop_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> bool:
    get_initiator_permission(journey_id, token=token, session=session)
    success = delete_journey_stop(session, journey_id, stop_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journey stop not found")
    return True
