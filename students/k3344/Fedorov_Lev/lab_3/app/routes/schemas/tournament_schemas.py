from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class TournamentBase(BaseModel):
    name: str
    tournament_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_deadline: Optional[date] = None
    description: Optional[str] = None
    season_id: Optional[int] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    tournament_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_deadline: Optional[date] = None
    description: Optional[str] = None
    season_id: Optional[int] = None

class TournamentResponse(TournamentBase):
    tournament_id: int

    class Config:
        from_attributes = True

