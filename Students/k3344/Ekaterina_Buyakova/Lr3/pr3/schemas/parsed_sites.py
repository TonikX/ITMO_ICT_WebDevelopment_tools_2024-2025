from pydantic import BaseModel


class ParsedSitesCreate(BaseModel):
    url: str
    title: str