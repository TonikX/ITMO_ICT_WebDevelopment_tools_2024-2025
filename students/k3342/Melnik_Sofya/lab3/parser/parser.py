import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()  

app = FastAPI()
semaphore = asyncio.Semaphore(10)

DB_CONFIG = {
    'database': os.getenv('POSTGRES_DB', 'finance_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '123456'),
    'host': os.getenv('POSTGRES_HOST', 'db'), 
    'port': os.getenv('POSTGRES_PORT', '5432')
}

class ParseRequest(BaseModel):
    urls: list[str]

async def insert_user(pool, username, email):
    async with semaphore:
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    'INSERT INTO "user" (username, email, hashed_password) VALUES ($1, $2, $3)',
                    username, email, 'fakepassword'
                )
            print(f'User {username} inserted into database')
        except Exception as e:
            print(f'Error inserting user {username}: {e}')

async def fetch(session, url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with session.get(url, headers=headers) as response:
        return await response.text()

async def parse_and_save(url, session, pool):
    try:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        user_links = soup.find_all('a', class_='tm-user-info__username')

        tasks = []
        for user in user_links:
            username = user.text.strip()
            email = f'{username}@habr.fake'
            tasks.append(insert_user(pool, username, email))

        await asyncio.gather(*tasks)
        print(f'Parsed users from {url}')
    except Exception as e:
        print(f'Error parsing {url}: {e}')

@app.post("/parse")
async def parse_urls(request: ParseRequest):
    try:
        pool = await asyncpg.create_pool(min_size=5, max_size=10, **DB_CONFIG)
        async with aiohttp.ClientSession() as session:
            tasks = [parse_and_save(url, session, pool) for url in request.urls]
            await asyncio.gather(*tasks)
        await pool.close()
        return {"status": "Parsing completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))