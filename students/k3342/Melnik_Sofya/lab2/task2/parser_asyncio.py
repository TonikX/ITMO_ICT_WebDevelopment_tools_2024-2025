import asyncio
import aiohttp
from bs4 import BeautifulSoup
import asyncpg
import time

DB_CONFIG = {
    'database': 'finance_db',
    'user': 'postgres',
    'password': '123456',
    'host': 'localhost',
    'port': '5434'
}

semaphore = asyncio.Semaphore(10)

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

async def parse_with_asyncio(urls):
    async with aiohttp.ClientSession() as session:
        pool = await asyncpg.create_pool(min_size=5, max_size=10, **DB_CONFIG)

        tasks = [parse_and_save(url, session, pool) for url in urls]
        await asyncio.gather(*tasks)

        await pool.close()

if __name__ == "__main__":
    urls = [
        'https://habr.com/ru/all/page16/',
        'https://habr.com/ru/all/page17/',
        'https://habr.com/ru/all/page18/',
        'https://habr.com/ru/all/page19/',
        'https://habr.com/ru/all/page20/',
    ]

    start_time = time.time()
    asyncio.run(parse_with_asyncio(urls))
    print(f"Asyncio time: {time.time() - start_time:.2f} seconds")