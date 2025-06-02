from datetime import time

from pydantic import BaseModel, Field


class GetUserSchema(BaseModel):
    id: int
    username: str
    is_admin: bool
