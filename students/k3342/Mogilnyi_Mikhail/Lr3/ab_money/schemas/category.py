from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class CategoryRead(CategoryBase):
    id: int

    class Config:
        orm_mode = True
