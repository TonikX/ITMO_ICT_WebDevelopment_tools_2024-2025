from pydantic import BaseModel

class SeasonBase(BaseModel):
    year: str


class SeasonCreate(SeasonBase):
    pass


class SeasonUpdate(SeasonBase):
    pass


class SeasonResponse(SeasonBase):
    season_id: int

    class Config:
        from_attributes = True
