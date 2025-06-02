from pydantic import BaseModel
from typing import List, Optional

class TeamBase(BaseModel):
    name: str
    coach: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    additional_info: Optional[str] = None
    school_id: Optional[int] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    coach: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    additional_info: Optional[str] = None
    school_id: Optional[int] = None


class TeamResponse(TeamBase):
    team_id: int
    user_id: int
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class TeamAdminUpdate(BaseModel):
    user_id: int