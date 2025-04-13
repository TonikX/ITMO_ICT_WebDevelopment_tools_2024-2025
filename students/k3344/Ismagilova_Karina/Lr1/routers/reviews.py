from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from auth.auth import authenticate_request
from models.models import Review, ReviewCreate
from db import get_session

router = APIRouter(prefix="/reviews", tags=["Reviews"], dependencies=[Depends(authenticate_request)])


@router.get("/", response_model=List[Review])
def get_all_reviews(session: Session = Depends(get_session)):
    return session.exec(select(Review)).all()


@router.get("/{review_id}", response_model=Review)
def get_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Такого отзыва нет")
    return review


@router.post("/", response_model=Review)
def create_review(review_data: ReviewCreate, session: Session = Depends(get_session)):
    review = Review(**review_data.dict())
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.patch("/{review_id}", response_model=Review)
def update_review(
    review_id: int,
    review_update: Review,
    session: Session = Depends(get_session)
):
    db_review = session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Такого отзыва нет")

    update_data = review_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None and value != "":
            setattr(db_review, key, value)

    session.commit()
    session.refresh(db_review)
    return db_review


@router.delete("/{review_id}")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Такого отзыва нет")
    session.delete(review)
    session.commit()
    return {"message": "Отзыв удалён"}
