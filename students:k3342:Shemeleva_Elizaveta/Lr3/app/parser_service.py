import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

import aiohttp
from sqlmodel import Session
from sqlalchemy.orm import sessionmaker

from .async_parser import parse_itmo, parse_spbpu, parse_expoforum
from .models import Task
from .database import engine_sync

logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(
    bind=engine_sync,
    expire_on_commit=False,
    class_=Session
)

class ParserService:
    PARSERS = {
        "student.itmo.ru": parse_itmo,
        "www.spbstu.ru": parse_spbpu,
        "www.expoforum.ru": parse_expoforum,
    }

    @classmethod
    async def parse_url(cls, url: str, save_to_db: bool = True) -> Dict[str, Any]:
        start = datetime.now()
        parser = cls._get_parser_for_url(url)
        if not parser:
            return {
                "success": False,
                "error": f"No parser for URL: {url}",
                "url": url,
                "events_count": 0,
                "duration": 0.0
            }

        # Открываем HTTP-сессию и передаём её в функцию-парсер
        async with aiohttp.ClientSession() as session:
            events: List[Task] = await parser(session, url)

        if save_to_db and events:
            cls._save_sync(events)

        duration = (datetime.now() - start).total_seconds()
        return {
            "success": True,
            "url": url,
            "events_count": len(events),
            "duration": duration,
            "events": [
                {"description": e.description, "due_date": e.due_date, "priority": e.priority.value}
                for e in events
            ]
        }

    @classmethod
    async def parse_multiple_urls(cls, urls: List[str], save_to_db: bool = True) -> List[Dict[str, Any]]:
        tasks = [cls.parse_url(u, save_to_db) for u in urls]
        return await asyncio.gather(*tasks)

    @classmethod
    def _get_parser_for_url(cls, url: str):
        for domain, parser in cls.PARSERS.items():
            if domain in url:
                return parser
        return None

    @classmethod
    def _save_sync(cls, events: List[Task]):
        try:
            with SessionLocal() as session:
                session.add_all(events)
                session.commit()
        except Exception as e:
            logger.error(f"Error saving to DB: {e}")
            raise
