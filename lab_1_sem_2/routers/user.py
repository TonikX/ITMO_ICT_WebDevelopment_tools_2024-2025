from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from db import get_session
from models import *

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/trips", response_model=list[TripWithDetails])
async def get_user_trips(user_id: int, session: Session = Depends(get_session)):
    trips = session.exec(
        select(Trip)
        .options(
            selectinload(Trip.user),
            selectinload(Trip.organizer)
        )
        .where(Trip.user_id == user_id)
    ).all()

    if not trips:
        raise HTTPException(status_code=404, detail="No trips found")

    return trips


@router.get("/{user_id}/trip_requests", response_model=list[TripRequestWithDetails])
async def get_user_trip_requests(user_id: int, session: Session = Depends(get_session)):
    trip_requests = session.exec(
        select(TripRequest)
        .options(
            selectinload(TripRequest.trip),
            selectinload(TripRequest.user)
        )
        .where(TripRequest.user_id == user_id)
    ).all()

    if not trip_requests:
        raise HTTPException(status_code=404, detail="No trip requests found")

    return trip_requests


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"status": 200, "message": "User deleted"}


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserRead])
def get_all_users(session: Session = Depends(get_session)):
    users = session.query(User).all()
    return users
