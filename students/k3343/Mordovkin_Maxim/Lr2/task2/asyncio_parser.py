import sys
import time
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# url для пароли admin и бд trip_db
db_url = "postgresql://postgres:admin@localhost:5432/trip_db"

url_list = [
    "https://stackoverflow.com",
    "https://www.djangoproject.com",
    "https://realpython.com",
    "https://docs.aiohttp.org",
    "https://pypi.org"
]

k = 4
timeout = 10

async def parse_and_save(url: str,
                         pool: asyncpg.Pool,
                         session: aiohttp.ClientSession,
                         sem: asyncio.Semaphore) -> None:
    async with sem:
        try:
            async with session.get(url, timeout=timeout) as resp:
                html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else ""

            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO pages (url, title) VALUES ($1, $2)",
                    url, title
                )

            print(f"{url} → «{title}»")
        except Exception as exc:
            print(f"[asyncio] error for {url}: {exc}")


async def run_async() -> float:
    start = time.perf_counter()
    async with asyncpg.create_pool(dsn=db_url, min_size=1, max_size=k) as pool:
        sem = asyncio.Semaphore(k)
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *(parse_and_save(u, pool, session, sem) for u in url_list)
            )
    return time.perf_counter() - start


if __name__ == "__main__":
    elapsed = asyncio.run(run_async())
    print(f"[asyncio] time: {elapsed:.3f} с")
