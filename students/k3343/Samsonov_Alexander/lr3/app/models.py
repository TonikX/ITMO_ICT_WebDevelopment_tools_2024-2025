from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel


class Story(SQLModel, table=True):
    __tablename__ = "stories"
    __table_args__ = {'extend_existing': True}
    id: int = Field(primary_key=True)
    by: Optional[str]
    time: datetime
    kids: Optional[List[int]] | None = Field(default=None, sa_column=Column(JSON))

    title: Optional[str]
    url: Optional[str]
    score: Optional[int]
    descendants: Optional[int]


class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}
    id: int = Field(primary_key=True)
    by: Optional[str]
    time: datetime
    kids: Optional[List[int]] | None = Field(default=None, sa_column=Column(JSON))

    text: Optional[str]
    parent: Optional[int]


class ListHolder(SQLModel, table=True):
    __tablename__ = "list_holder"
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    new_ids: list[int] = Field(sa_column=Column(ARRAY(Integer)))
    trending_ids: list[int] = Field(sa_column=Column(ARRAY(Integer)))
