from sqlmodel import SQLModel

from core.models import CoreModel


class User(CoreModel, table=True):
    email: str
    password: str


class JWTPayload(SQLModel):
    sub: str
    exp: float
    iat: float
