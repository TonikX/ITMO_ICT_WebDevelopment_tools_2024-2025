from pydantic import BaseModel, ConfigDict


class CoreDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        from_attributes=True,
    )
