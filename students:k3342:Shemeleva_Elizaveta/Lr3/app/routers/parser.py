import httpx
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from ..parser_service import ParserService

router = APIRouter(prefix="/parse", tags=["parser"])

class SupportedSites(str, Enum):
    ITMO = "https://student.itmo.ru/ru/events/"
    SPBSTU = "https://www.spbstu.ru/media/announcements/"
    EXPOFORUM = "https://www.expoforum.ru/calendar/"

class SaveToDbOption(str, Enum):
    YES = "true"
    NO = "false"

class ParseRequest(BaseModel):
    url: str

class ParseResponse(BaseModel):
    success: bool
    message: str
    url: str
    events_count: int
    duration: float
    timestamp: datetime
    events: Optional[List[dict]] = None

@router.post("/", response_model=ParseResponse)
async def parse_url(
    url: SupportedSites = Query(..., description="Выберите сайт для парсинга"),
    save_to_db: SaveToDbOption = Query(
        SaveToDbOption.YES, description="Сохранять результат в БД?"
    ),
):
    save_flag = (save_to_db == SaveToDbOption.YES)
    result = await ParserService.parse_url(url.value, save_flag)
    return ParseResponse(
        success=result["success"],
        message="Parsing completed" if result["success"] else f"Error: {result.get('error')}",
        url=result["url"],
        events_count=result["events_count"],
        duration=result["duration"],
        timestamp=datetime.now(),
        events=result.get("events") if save_flag else [],
    )

@router.post("/bulk")
async def parse_bulk_urls(
    urls: List[SupportedSites] = Query(..., description="Выберите сайты для парсинга"),
    save_to_db: SaveToDbOption = Query(
        SaveToDbOption.YES, description="Сохранять результат в БД?"
    ),
):
    url_strings = [site.value for site in urls]
    save_flag = (save_to_db == SaveToDbOption.YES)
    results = await ParserService.parse_multiple_urls(url_strings, save_flag)
    return {
        "total_urls": len(urls),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "total_events": sum(r["events_count"] for r in results),
        "results": results,
    }

@router.get("/supported-sites")
async def get_supported_sites():
    return {
        "supported_domains": ParserService.get_supported_domains(),
        "total_parsers": len(ParserService.get_supported_domains()),
    }

@router.post("/predefined")
async def parse_predefined_urls(save_to_db: bool = Query(True)):
    predefined_urls = [
        "https://student.itmo.ru/ru/events/",
        "https://www.spbstu.ru/media/announcements/",
        "https://www.expoforum.ru/calendar/",
    ]
    results = await ParserService.parse_multiple_urls(predefined_urls, save_to_db)
    return {
        "message": "Predefined URLs parsed",
        "results": results,
        "total_events": sum(r["events_count"] for r in results),
    }
