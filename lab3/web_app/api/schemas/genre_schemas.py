from typing import Optional

from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: int
    name: str


class GenreCreateAndUpdate(BaseModel):
    name: str
