from typing import Annotated
from pydantic import AfterValidator, BaseModel, HttpUrl


class ParseUrlDTO(BaseModel):
    url: Annotated[HttpUrl, AfterValidator(str)]
