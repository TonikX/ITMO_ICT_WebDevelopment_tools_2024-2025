from typing import Annotated
from fastapi import APIRouter, Depends, status

from parsers.depends import get_parser_service
from parsers.dtos import ParseUrlDTO
from parsers.services import ParserService

router = APIRouter(prefix="/parsers")


@router.post("/", status_code=status.HTTP_200_OK)
async def parse(
    service: Annotated[ParserService, Depends(get_parser_service)],
    dto: ParseUrlDTO,
    async_parse: bool = False,
):
    await service.parse(dto, is_async=async_parse)
    return {"message": "ok"}
