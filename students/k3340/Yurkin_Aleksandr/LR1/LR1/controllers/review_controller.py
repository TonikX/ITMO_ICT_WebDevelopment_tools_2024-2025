from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List

from connection import get_session
from models.review_model import Review, ReviewDetails
from models.trip_model import Trip
from models.user_model import User
from util.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=Review)
def create_review(
    trip_id: int,
    rating: int,
    comment: str = None,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session)
):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    new_review = Review(trip_id=trip_id, user_id=current_user.id, rating=rating, comment=comment)
    session.add(new_review)
    session.commit()
    session.refresh(new_review)
    return new_review

@router.get("/trip/{trip_id}", response_model=List[ReviewDetails])
def list_reviews_for_trip(trip_id: int, session=Depends(get_session)):
    reviews = session.exec(select(Review).where(Review.trip_id == trip_id)).all()
    return reviews
