import logging
import os

import aiohttp
import asyncpg
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()


async def get_db_connection():
    return await asyncpg.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )


async def ensure_table_exists(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS async (
            id serial PRIMARY KEY,
            url text,
            title text
        )
    ''')


async def parse_and_save(url: str) -> str | None:
    conn = None
    try:
        conn = await get_db_connection()
        await ensure_table_exists(conn)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string if soup.title else 'No title'

                await conn.execute(
                    "INSERT INTO async (url, title) VALUES ($1, $2)",
                    url, title
                )

                logger.info(f"Successfully parsed and saved: {url}")
                return title
    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}")
        raise
    finally:
        if conn:
            await conn.close()


@app.get("/parse/")
async def parse(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        title = await parse_and_save(url)
        return {"message": "Parsing completed", "title": title}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
