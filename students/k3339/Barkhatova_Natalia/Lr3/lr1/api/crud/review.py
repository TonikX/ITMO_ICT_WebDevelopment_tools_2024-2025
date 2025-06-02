from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from db import get_session
from models.review import Review as ReviewModel
from schemas.review import Review as ReviewSchema, ReviewCreate, ReviewUpdate

router = APIRouter()


@router.post("/reviews/", response_model=ReviewSchema)
def create_review(review: ReviewCreate, session: Session = Depends(get_session)) -> ReviewSchema:
    db_review = ReviewModel(**review.dict())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return ReviewSchema.from_orm(db_review)


@router.get("/reviews/{review_id}", response_model=ReviewSchema)
def read_review(review_id: int, session: Session = Depends(get_session)) -> ReviewSchema:
    db_review = session.get(ReviewModel, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewSchema.from_orm(db_review)


@router.get("/reviews/", response_model=List[ReviewSchema])
def read_reviews(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)) -> List[ReviewSchema]:
    db_reviews = session.query(ReviewModel).offset(skip).limit(limit).all()
    return [ReviewSchema.from_orm(r) for r in db_reviews]


@router.patch("/reviews/{review_id}", response_model=ReviewSchema)
def update_review(review_id: int, review: ReviewUpdate, session: Session = Depends(get_session)) -> ReviewSchema:
    db_review = session.get(ReviewModel, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in review.dict(exclude_unset=True).items():
        setattr(db_review, key, value)

    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return ReviewSchema.from_orm(db_review)


@router.delete("/reviews/{review_id}", response_model=ReviewSchema)
def delete_review(review_id: int, session: Session = Depends(get_session)) -> ReviewSchema:
    db_review = session.get(ReviewModel, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    response: ReviewSchema = ReviewSchema.from_orm(db_review)
    session.delete(db_review)
    session.commit()
    return response
