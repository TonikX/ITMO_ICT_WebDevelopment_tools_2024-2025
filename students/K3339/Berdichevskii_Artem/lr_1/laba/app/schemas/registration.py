from enum import Enum

from pydantic import BaseModel


class Skill(str, Enum):
    programmer = "programmer"
    analyst = "analyst"
    designer = "designer"


class EventDisplay(BaseModel):
    id: int
    title: str
    description: str


class UserDisplay(BaseModel):
    id: int
    username: str


class TeamDisplay(BaseModel):
    id: int
    name: str
    description: str


class RegistrationBase(BaseModel):
    name: str
    address: str
    phone_number: str
    skill: Skill


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationCreateInternal(RegistrationCreate):
    event_id: int
    user_id: int
    team_id: int


class RegistrationUpdate(RegistrationBase):
    confirmed: bool


class RegistrationDisplay(RegistrationBase):
    id: int
    event: EventDisplay
    user: UserDisplay
    team: TeamDisplay
