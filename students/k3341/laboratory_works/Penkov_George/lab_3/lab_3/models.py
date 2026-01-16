from pydantic import BaseModel, PositiveInt


class BookCreate(BaseModel):
    title: str
    year: PositiveInt | None = None
    description: str | None = None
    author_id: int | None = None
    genre_ids: list[int] = []
