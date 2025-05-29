import os
from dotenv import load_dotenv
from fastapi import HTTPException
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .model import TripRealParser

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/trip_db")
async_engine = create_async_engine(DB_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)



async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=f"Ошибка при загрузке {url}")
        return await response.text()

def extract_tours_from_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    tour_cards = soup.find_all("div", class_="js-ao-serp-tour-card")
    results = []

    for card in tour_cards:
        try:
            title_tag = card.find("h3", class_="ao-serp-tour-card__title")
            title = title_tag.get_text(strip=True) if title_tag else None

            destination_tag = card.find("dt", string="Destinations")
            destination = destination_tag.find_next("dd").get_text(strip=True).split(",")[0] if destination_tag else None

            age_tag = card.find("dt", string="Age Range")
            age_range = age_tag.find_next("dd").get_text(strip=True) if age_tag else None

            duration_block = card.find("dl", class_="ao-serp-tour-card__detail-item--duration")
            duration_days = duration_block.find("dd").get_text(strip=True) if duration_block else None

            if not all([title, destination, age_range, duration_days]):
                continue

            results.append({
                "title": title,
                "destination": destination,
                "age": age_range,
                "duration": duration_days
            })
        except Exception:
            continue

    return results

async def parse_tour_page(url: str) -> list[dict]:
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            html = await fetch(session, url)
            return extract_tours_from_html(html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга {url}: {str(e)}")

async def save_tours_to_db(tours: list[dict]):
    async with AsyncSessionLocal() as session:
        for tour in tours:
            trip_db = TripRealParser(**tour)
            session.add(trip_db)
        await session.commit()
    return len(tours)

async def parse_and_save_tours(url: str):
    try:
        tours = await parse_tour_page(url)
        count = await save_tours_to_db(tours)
        return count
    except HTTPException:
        raise
    except Exception as e:
        raise Exception(f"Ошибка обработки данных: {str(e)}")
