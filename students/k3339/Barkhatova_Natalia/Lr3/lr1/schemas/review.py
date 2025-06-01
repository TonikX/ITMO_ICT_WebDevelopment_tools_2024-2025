from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReviewCreate(ReviewBase):
    user_id: int
    reviewed_user_id: int

    class Config:
        orm_mode = True


class ReviewUpdate(ReviewBase):
    rating: Optional[int] = None
    comment: Optional[str] = None
    reviewed_user_id: Optional[int] = None

    class Config:
        orm_mode = True


class Review(ReviewBase):
    user_id: int
    reviewed_user_id: int
    id: int

    class Config:
        orm_mode = True
