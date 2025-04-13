from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from connection import get_session
from models.models import FavoriteTrip, Trip

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.get("/user/{user_id}", response_model=List[Trip])
def get_user_favorites(user_id: int, db: Session = Depends(get_session)):
    stmt = select(Trip).join(FavoriteTrip).where(FavoriteTrip.user_id == user_id)
    return db.exec(stmt).all()

@router.post("")
def add_favorite_trip(user_id: int, trip_id: int, db: Session = Depends(get_session)):
    existing = db.get(FavoriteTrip, (user_id, trip_id))
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")
    db.add(FavoriteTrip(user_id=user_id, trip_id=trip_id))
    db.commit()
    return {"message": "Added to favorites"}

@router.delete("")
def remove_favorite_trip(user_id: int, trip_id: int, db: Session = Depends(get_session)):
    favorite = db.get(FavoriteTrip, (user_id, trip_id))
    if not favorite:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(favorite)
    db.commit()
    return {"message": "Removed from favorites"}
