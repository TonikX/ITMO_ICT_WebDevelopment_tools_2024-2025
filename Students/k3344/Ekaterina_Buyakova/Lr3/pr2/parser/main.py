import asyncio
import logging
import os
from asyncio import StreamWriter, StreamReader
from typing import Callable, Awaitable
from urllib.parse import urlparse

import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def create_aiohttp_session():
    return aiohttp.ClientSession()


async def create_async_table(db_pool: asyncpg.pool.Pool):
    async with db_pool.acquire() as conn:
        await conn.execute('\n'
                           '                           CREATE TABLE IF NOT EXISTS async\n'
                           '                           (id serial PRIMARY KEY,\n'
                           '                            url text,\n'
                           '                            title text\n'
                           '                           )')


def is_url(data: str):
    parsed = urlparse(data)
    return parsed.scheme and parsed.netloc


async def parse_and_save(writer: StreamWriter, session: aiohttp.ClientSession, db_pool: asyncpg.pool.Pool, url: str) -> \
        Awaitable[None] | None:
    result = ""
    if not is_url(url):
        result = 'Invalid url'
        logger.info(f"Skipping {url}")
    else:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else 'No title'
            result = title or 'None'

            async with db_pool.acquire() as connection:
                await connection.execute(
                    "INSERT INTO async (url, title) VALUES ($1, $2)", url, title
                )
            logger.info(f"Saved: url {url}, title {title}")

    writer.write(result.encode())
    await writer.drain()

    logger.debug(f"Sent: {result}")

    writer.close()
    await writer.wait_closed()


def handler(session: aiohttp.ClientSession, db_pool: asyncpg.pool.Pool) -> Callable[
    [StreamReader, StreamWriter], Awaitable[None] | None]:
    async def wrapper(reader: StreamReader, writer: StreamWriter):
        logger.info(f"Connection from {writer.get_extra_info('peername')}")
        recv_data = await reader.readline()
        print(recv_data, type(recv_data))
        recv_data = recv_data.decode("utf-8").strip()

        logger.debug(f"recv_data: {recv_data}")

        task = asyncio.create_task(parse_and_save(writer, session, db_pool, recv_data))
        await asyncio.gather(task)
        return

    return wrapper


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    db_pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

    try:
        await create_async_table(db_pool)
        async with create_aiohttp_session() as session:
            server = await asyncio.start_server(
                handler(session, db_pool),
                host=os.getenv("PARSER_HOST"),
                port=os.getenv("PARSER_PORT")
            )
            async with server:
                logger.info(f"Server running on {server}")
                await server.serve_forever()
    except Exception as error:
        logger.error(error)
    finally:
        await db_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
