import aiohttp
from bs4 import BeautifulSoup
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

async def parse_and_save_async(session, url, table_name="specializations"):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                print(f"ошибка для {url}")
                return

            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')

            name = soup.find('h1').get_text(strip=True)
            description = soup.find('p').get_text(strip=True)

            conn = psycopg2.connect(**DB_PARAMS)
            cur = conn.cursor()
            cur.execute(f"INSERT INTO {table_name} (name, description) VALUES (%s, %s)", (name, description))
            conn.commit()
            cur.close()
            conn.close()

            print(f"Saved {name}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
