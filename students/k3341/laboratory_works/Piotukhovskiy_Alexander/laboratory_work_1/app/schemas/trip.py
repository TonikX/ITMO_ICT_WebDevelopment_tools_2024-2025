from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

from db.models import TripRole, TripStatus
from schemas.user import UserResponse, TripResponse


class TripCreate(BaseModel):
    title: str
    description: str
    departure: datetime
    arrival: Optional[datetime] = None
    departure_location: str
    arrival_location: str


class TripUpdate(BaseModel):
    title: str
    description: str
    departure: datetime
    arrival: Optional[datetime] = None
    departure_location: str
    arrival_location: str


class TripParticipationResponse(BaseModel):
    id: UUID
    trip_id: UUID
    user_id: UUID
    role: TripRole
    status: TripStatus
    joined_at: datetime

    model_config = {"from_attributes": True}


class TripDetailResponse(TripResponse):
    creator: UserResponse
    participants: List[UserResponse] = []

    model_config = {"from_attributes": True}


class TripSearchDto(BaseModel):
    title: Optional[str] = None
    departure: Optional[datetime] = None
    arrival: Optional[datetime] = None
    departure_location: Optional[str] = None
    arrival_location: Optional[str] = None
    creator_id: Optional[UUID] = None
    departure_from: Optional[datetime] = None
    departure_to: Optional[datetime] = None
