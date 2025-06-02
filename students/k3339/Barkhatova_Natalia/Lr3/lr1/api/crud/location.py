from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from db import get_session
from models import Location as LocationModel
from schemas.location import Location as LocationSchema, LocationCreate, LocationUpdate

router = APIRouter()


@router.post("/locations/", response_model=LocationSchema)
def create_location(
        location: LocationCreate, session: Session = Depends(get_session)
) -> LocationSchema:
    db_location = LocationModel(**location.dict())
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    return LocationSchema.from_orm(db_location)


@router.get("/locations/{location_id}", response_model=LocationSchema)
def read_location(
        location_id: int, session: Session = Depends(get_session)
) -> LocationSchema:
    db_location = session.get(LocationModel, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationSchema.from_orm(db_location)


@router.get("/locations/", response_model=List[LocationSchema])
def read_locations(
        skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
) -> List[LocationSchema]:
    db_locations = session.query(LocationModel).offset(skip).limit(limit).all()
    return [LocationSchema.from_orm(loc) for loc in db_locations]


@router.patch("/locations/{location_id}", response_model=LocationSchema)
def update_location(
        location_id: int, location: LocationUpdate, session: Session = Depends(get_session)
) -> LocationSchema:
    db_location = session.get(LocationModel, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    for key, value in location.dict(exclude_unset=True).items():
        setattr(db_location, key, value)

    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    return LocationSchema.from_orm(db_location)


@router.delete("/locations/{location_id}", response_model=LocationSchema)
def delete_location(
        location_id: int, session: Session = Depends(get_session)
) -> LocationSchema:
    db_location = session.get(LocationModel, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    response: LocationSchema = LocationSchema.from_orm(db_location)
    session.delete(db_location)
    session.commit()
    return response
