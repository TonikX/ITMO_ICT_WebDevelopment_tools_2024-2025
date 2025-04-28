import aiohttp
import asyncio
from bs4 import BeautifulSoup
import psycopg2

DB_PARAMS = {
    "dbname": "psychologists_db",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5433"
}

async def parse_and_save_async(session, url, table_name="specializations_async"):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                print(f"Failed to fetch {url} with status {response.status}")
                return

            text = await response.text()

            soup = BeautifulSoup(text, 'html.parser')

            title_tag = soup.find('h1')
            name = title_tag.get_text(strip=True) if title_tag else 'No Title'

            description_tag = soup.find('p')
            description = description_tag.get_text(strip=True) if description_tag else 'No Description'

            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()

            cursor.execute(
                f'''
                INSERT INTO {table_name} (name, description)
                VALUES (%s, %s)
                ''',
                (name, description)
            )

            conn.commit()
            cursor.close()
            conn.close()

            print(f"Saved {name} from {url}")

    except Exception as e:
        print(f"Error processing {url}: {e}")
