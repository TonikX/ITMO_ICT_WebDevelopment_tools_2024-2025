import asyncio
import logging
import os

import aiohttp
import asyncpg
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def parse_and_save(url: str) -> None:
    logger.info("Start async parse: %s", url)
    connection: asyncpg.Connection = await asyncpg.connect(os.getenv("POSTGRES_URL"))
    logger.info("Connected to database")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                logger.error("Parse failed: %s", url)
                return

            soup = BeautifulSoup(await response.text(), features="html.parser")
            title = soup.find("title").text
            logger.info("Page title: %s", title)

            skills: set[str] = set()
            for row in soup.find("table").find("tbody").find_all("tr"):
                skill = row.get_text().split()[1]
                skills.add(skill)

            query = """INSERT INTO skill VALUES (DEFAULT, $1)
                ON CONFLICT (name) DO NOTHING;"""

            await connection.executemany(query, map(lambda skill: (skill,), skills))
            logger.info("Skills saved")

    await connection.close()
    logger.info("End async parse: %s", url)


async def main(urls: list[str]) -> None:
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(parse_and_save(url))
