from sqlmodel import SQLModel, Field
from typing import Optional

class TripRealParser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    destination: str
    age: str
    duration: str
