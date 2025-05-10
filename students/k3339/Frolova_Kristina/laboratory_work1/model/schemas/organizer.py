from sqlmodel import SQLModel

class OrganizerRead(SQLModel):
    user_id: int
    hackathon_id: int
