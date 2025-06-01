from typing import Optional

from pydantic import BaseModel


class LocationBase(BaseModel):
    city: str
    region: Optional[str] = None

    class Config:
        orm_mode = True


class LocationCreate(LocationBase):
    user_id: int


class LocationUpdate(LocationBase):
    city: Optional[str] = None
    region: Optional[str] = None


class Location(LocationBase):
    id: int

    class Config:
        orm_mode = True
