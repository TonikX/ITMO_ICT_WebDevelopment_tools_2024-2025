from fastapi import FastAPI, HTTPException
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from db_async import create_user_record

load_dotenv()

app = FastAPI()

BASE_URL = "https://itmo.ru"
LETTERS = [
    ("А", "/ru/personlist/192/letter_192.htm"),
    ("Б", "/ru/personlist/193/letter_193.htm"),
]

DATABASE_DSN = os.environ["DB_URL_FOR_PARSER"]

async def parse_and_save(session, pool, url):
    try:
        async with session.get(url, timeout=10) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            people_links = soup.select("a.contact-pad.-person-list")
            async with pool.acquire() as conn:
                for person_link in people_links:
                    name_tag = person_link.select_one("h4.name")
                    if name_tag:
                        name = name_tag.get_text(strip=True)
                        if name:
                            await create_user_record(conn, name)
    except Exception as e:
        print(f"Error: {e}")
        raise e

@app.post("/parse")
async def parse():
    try:
        pool = await asyncpg.create_pool(DATABASE_DSN, min_size=2, max_size=10)
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _, path in LETTERS:
                url = BASE_URL + path
                tasks.append(parse_and_save(session, pool, url))

            await asyncio.gather(*tasks)
        await pool.close()

        return {"message": "Parsing completed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
