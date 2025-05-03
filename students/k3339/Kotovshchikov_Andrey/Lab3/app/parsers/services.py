from fastapi import HTTPException, status
import httpx
from parsers.dtos import ParseUrlDTO
from core.config import settings


class ParserService:
    async def parse(self, dto: ParseUrlDTO, is_async: bool = False) -> None:
        try:
            async with httpx.AsyncClient(base_url=settings.PARSER_URL) as client:
                url = "/parse" if not is_async else "/parse/async"
                response = await client.post(url, params=dto.model_dump(mode="json"))
                if not response.is_success:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Parser not available",
                    )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Parser not available",
            )
