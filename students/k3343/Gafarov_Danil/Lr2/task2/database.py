# database.py

from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.orm import Session
from sqlalchemy import text

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True)
    hashed_password: str = Field(default="parsed")

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/team_finder"
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)

def clear_users():
    with get_session() as session:
        session.execute(text('DELETE FROM "user"'))
        session.commit()