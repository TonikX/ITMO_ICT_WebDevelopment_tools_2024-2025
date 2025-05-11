from sqlmodel import SQLModel


class TagCreate(SQLModel):
    name: str


class TagRead(SQLModel):
    id: int
    name: str
