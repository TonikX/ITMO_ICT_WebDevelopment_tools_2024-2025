import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Country, Trip
import ssl

DATABASE_URL = "postgresql+asyncpg://lr3:12345678@localhost:7432/lr3"
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def parse_and_save_async(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=10, ssl=ssl_context) as resp:
            resp.raise_for_status()
            html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')
        country_name = soup.find_all('a', itemprop='item')[1].get_text(strip=True)
        hotels = [
            p.get_text(strip=True)
            for p in soup.find_all('p', class_="HotelTitle_descriptionTitle___uwHg")
        ]

        async with AsyncSessionLocal() as db:
            async with db.begin():
                result = await db.execute(
                    select(Country).where(Country.name == country_name)
                )
                country = result.scalar_one_or_none()
                if not country:
                    country = Country(name=country_name)
                    db.add(country)
                    await db.flush()

                for title in hotels:
                    trip = Trip(
                        title=title,
                        destination=country_name,
                        country_id=country.id,
                    )
                    db.add(trip)
    except Exception as e:
        print(f"Error for {url}: {e}")


async def async_parse_and_save(url: str, session: aiohttp.ClientSession, SessionLocal):
    try:
        async with session.get(url, timeout=10, ssl=ssl_context) as resp:
            resp.raise_for_status()
            html = await resp.text()

        soup = BeautifulSoup(html, 'html.parser')
        country_name = soup.find_all('a', itemprop='item')[1].get_text(strip=True)
        hotels = [
            p.get_text(strip=True)
            for p in soup.find_all('p', class_="HotelTitle_descriptionTitle___uwHg")
        ]

        async with SessionLocal.begin():
            result = await SessionLocal.execute(
                select(Country).where(Country.name == country_name)
            )
            country = result.scalar_one_or_none()
            if not country:
                country = Country(name=country_name)
                SessionLocal.add(country)
                await SessionLocal.flush()

            for title in hotels:
                trip = Trip(
                    title=title,
                    destination=country_name,
                    country_id=country.id,
                )
                SessionLocal.add(trip)
    except Exception as e:
        print(f"Error for {url}: {e}")


async def async_run(urls):
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with aiohttp.ClientSession() as session:
        tasks = [async_parse_and_save(url, session, AsyncSessionLocal) for url in urls]
        await asyncio.gather(*tasks)
    await engine.dispose()


def run(urls):
    async def _wrap():
        start = time.perf_counter()
        await async_run(urls)
        return time.perf_counter() - start

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_wrap())
    else:
        return _wrap()