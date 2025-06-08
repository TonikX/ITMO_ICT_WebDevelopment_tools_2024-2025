from pydantic import BaseModel
from typing import List, Optional


class Profession(BaseModel):
    id: int
    title: str
    description: str


class Skill(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""


class Warrior(BaseModel):
    id: int
    race: str
    name: str
    level: int
    profession: Profession
    skills: List[Skill] = []


class BlogComment(BaseModel):
    id: int
    content: str
    author: str


class BlogArticle(BaseModel):
    id: int
    title: str
    author: str
    comments: List[BlogComment] = []