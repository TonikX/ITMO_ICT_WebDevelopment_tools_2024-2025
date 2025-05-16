import os
import time
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
DB_DSN = os.getenv("DB_ADMIN")  # e.g. "postgresql://user:pass@host:port/dbname"
URLS = [
    'https://hackathons.pro/tpost/jmg3d12jj1-hakaton-vkrum-ot-rtu-mirea-vk-i-rustore',
    'https://hackathons.pro/tpost/220m4u3631-hakaton-po-prompt-inzhiniringu-eksprompt',
    'https://hackathons.pro/tpost/7i620ksj51-vserossiiskii-hakaton-fits-2024'
]
NUM_WORKERS = 4

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

async def fetch_html(session: aiohttp.ClientSession, url: str):
    async with session.get(url, headers=HEADERS) as resp:
        return resp.status, await resp.text()

async def parse_and_save(url: str, http: aiohttp.ClientSession, pg_pool: asyncpg.Pool):
    status, html = await fetch_html(http, url)
    if status != 200:
        print(f"[async] Ошибка {status} при запросе {url}")
        return

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title else None
    meta = (
        soup.find('meta', attrs={'name': 'description'}) or
        soup.find('meta', attrs={'property': 'og:description'})
    )
    description = meta['content'].strip() if meta and meta.has_attr('content') else None

    # Записываем через asyncpg
    async with pg_pool.acquire() as conn:
        await conn.execute(
            '''
            INSERT INTO hackathon (title, description)
            VALUES ($1, $2)
            ''',
            title or 'N/A',
            description
        )

    print(f"[async] {url} → title: {title!r}; desc: {description!r}")

async def main():
    t0 = time.perf_counter()

    # создаём пул соединений к БД
    pg_pool = await asyncpg.create_pool(
        dsn=DB_DSN,
        min_size=1,
        max_size=NUM_WORKERS,
        max_inactive_connection_lifetime=30
    )

    # один aiohttp-сессия для всех запросов
    async with aiohttp.ClientSession() as http:
        sem = asyncio.Semaphore(NUM_WORKERS)

        async def worker(u):
            async with sem:
                await parse_and_save(u, http, pg_pool)

        await asyncio.gather(*(worker(u) for u in URLS))

    # закрываем пул
    await pg_pool.close()

    print(f"[asyncio+asyncpg] Time= {time.perf_counter() - t0:.3f}s")

if __name__ == '__main__':
    asyncio.run(main())