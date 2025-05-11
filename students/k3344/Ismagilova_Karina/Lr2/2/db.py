from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/trip_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TripRealParser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    destination: str
    age: str
    duration: str

SQLModel.metadata.create_all(engine)
