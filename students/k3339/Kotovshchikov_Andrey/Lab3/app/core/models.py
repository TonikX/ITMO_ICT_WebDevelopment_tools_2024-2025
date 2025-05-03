from sqlmodel import Field, SQLModel


class CoreModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
