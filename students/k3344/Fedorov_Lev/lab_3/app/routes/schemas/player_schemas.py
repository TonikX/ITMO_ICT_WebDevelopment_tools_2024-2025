from datetime import date
from typing import Optional

from pydantic import BaseModel


class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    country: Optional[str] = None
    city: Optional[str] = None
    gender: Optional[str] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    additional_info: Optional[str] = None
    photo_url: Optional[str] = None
    snils: Optional[int] = None
    birth_certificate: Optional[str] = None
    consent: bool = False


class PlayerCreate(PlayerBase):
    team_id: Optional[int] = None


class PlayerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    country: Optional[str] = None
    city: Optional[str] = None
    gender: Optional[str] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    additional_info: Optional[str] = None
    photo_url: Optional[str] = None
    team_id: Optional[int] = None


class PlayerResponse(PlayerBase):
    player_id: int
    team_id: Optional[int] = None
    team_name: Optional[str] = None

    class Config:
        from_attributes = True


class TeamBriefResponse(BaseModel):
    team_id: int
    name: str

    class Config:
        from_attributes = True


class PlayerDetailResponse(PlayerResponse):
    team: Optional[TeamBriefResponse] = None

