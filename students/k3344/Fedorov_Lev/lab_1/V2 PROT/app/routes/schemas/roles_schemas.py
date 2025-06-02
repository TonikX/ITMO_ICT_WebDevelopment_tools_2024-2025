from pydantic import BaseModel


class RoleCreate(BaseModel):
    role_name: str


class RoleResponse(BaseModel):
    role_id: int
    role_name: str

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    role_name: str


class RoleAssignment(BaseModel):
    user_id: int
    role_id: int
