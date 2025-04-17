from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, conint, Field, field_validator


class UserRegistration(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = {"from_attributes": True}


class SkillResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class UserSkillResponse(BaseModel):
    skill: SkillResponse
    proficiency: int

    model_config = {"from_attributes": True}


class TripResponse(BaseModel):
    id: UUID
    title: str
    description: str
    departure: datetime
    arrival: Optional[datetime] = None
    departure_location: str
    arrival_location: str

    model_config = {"from_attributes": True}


class ExtendedUserResponse(UserResponse):
    skills: List[UserSkillResponse] = Field(default_factory=list, alias="user_skills")
    created_trips: List[TripResponse] = Field(default_factory=list)
    participated_trips: List[TripResponse] = Field(default_factory=list, alias="trip_participations")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

    @field_validator("participated_trips", mode="before")
    def extract_trip(cls, value):
        return [item.trip for item in value if item.trip is not None]


class UserAuthResponse(BaseModel):
    user: UserResponse
    access_token: str


class UserLogin(BaseModel):
    login: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class SkillAdd(BaseModel):
    skill_id: UUID
    proficiency: Optional[conint(ge=1, le=10)] = 1


class UserSkillsUpdate(BaseModel):
    add: Optional[List[SkillAdd]] = []
    remove: Optional[List[UUID]] = []
