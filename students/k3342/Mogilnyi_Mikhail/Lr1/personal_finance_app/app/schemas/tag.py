from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagRead(TagBase):
    id: int

    class Config:
        orm_mode = True

class TagUpdate(BaseModel):
    name: Optional[str] = None
