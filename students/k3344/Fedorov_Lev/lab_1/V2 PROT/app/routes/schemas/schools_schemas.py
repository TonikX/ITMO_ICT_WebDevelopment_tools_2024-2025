from typing import List, Optional
from pydantic import BaseModel

class SportSchoolBase(BaseModel):
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    contact_info: Optional[str] = None


class SportSchoolCreate(SportSchoolBase):
    pass


class SportSchoolUpdate(SportSchoolBase):
    name: Optional[str] = None


class SportSchoolResponse(SportSchoolBase):
    school_id: int

    class Config:
        from_attributes = True
