from pydantic import BaseModel


class ParseRequest(BaseModel):
    url: str
    table_name: str = "specializations"
