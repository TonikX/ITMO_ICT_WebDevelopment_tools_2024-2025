from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(default="acc1", unique=True, index=True, nullable=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    registrations: List["Registration"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin'})
