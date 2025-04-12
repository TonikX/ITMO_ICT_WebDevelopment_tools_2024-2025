from sqlmodel import SQLModel


class TeamCreate(SQLModel):
    name: str