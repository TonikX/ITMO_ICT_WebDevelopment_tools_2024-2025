from typing import Optional

from sqlmodel import SQLModel

class ParticipantCreate(SQLModel):
    hackathon_id: int

class ParticipantRead(SQLModel):
    id: int
    hackathon_id: int
    user_id: int
    team_id: Optional[int]
    is_approved: bool

class ParticipantJoinTeam(SQLModel):
    participant_id: int
    team_id: int