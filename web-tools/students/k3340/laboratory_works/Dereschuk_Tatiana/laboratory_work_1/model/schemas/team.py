from pydantic import BaseModel
from typing_extensions import Optional

from model.schemas.project import ProjectRead


class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    project_id: int

class TeamRead(TeamBase):
    id: int
    project: ProjectRead

    class Config:
        from_attributes = True

class TeamUpdate(TeamBase):
    name: Optional[str]