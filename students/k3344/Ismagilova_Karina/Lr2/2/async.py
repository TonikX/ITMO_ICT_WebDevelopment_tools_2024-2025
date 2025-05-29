import asyncio
import aiohttp
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from db import TripRealParser
from parser import extract_tours_from_html, URLS

async_engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/trip_db")
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def parse_tour_page_async(url):
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                html = await response.text()
                return extract_tours_from_html(html)
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return []

async def parse_and_save_async(url):
    tours = await parse_tour_page_async(url)
    async with AsyncSessionLocal() as session:
        for data in tours:
            trip = TripRealParser(**data)
            session.add(trip)
        await session.commit()
        print(f"Сохранено: {len(tours)} туров с {url}")

async def main():
    tasks = [parse_and_save_async(url) for url in URLS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(main())
    print(f"Время выполнения Async: {time.time() - start:.7f} сек")
