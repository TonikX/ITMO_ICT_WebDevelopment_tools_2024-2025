from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class OrganizerProfile(BaseModel):
    id: int
    bio: Optional[str]
    experience: Optional[str]
    travel_preferences: Optional[str]


class TripParticipant(BaseModel):
    id: int
    name: str
    message: Optional[str]


class Trip(BaseModel):
    id: int
    title: str
    organizer_name: str
    start_location: str
    end_location: str
    start_date: date
    end_date: date
    organizer_profile: OrganizerProfile
    participants: List[TripParticipant]
