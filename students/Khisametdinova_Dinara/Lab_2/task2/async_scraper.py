import asyncio
import aiohttp
import time
import psycopg2
from bs4 import BeautifulSoup

DB_PARAMS = {
    "dbname": "psychologists_db",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5433"
}

SEM = asyncio.Semaphore(10)  

async def parse_and_save(session, url, table_name="specializations_async"):
    async with SEM:  # не больше 10 запросов одновременно
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    print(f"Failed {url} - Status {response.status}")
                    return

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                title_tag = soup.find('h1')
                name = title_tag.get_text(strip=True) if title_tag else "No Title"

                first_paragraph = soup.find('p')
                description = first_paragraph.get_text(strip=True) if first_paragraph else "No Description"

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

                await asyncio.sleep(0.1) 

        except Exception as e:
            print(f"Error processing {url}: {e}")

async def main():
    with open('specialization_urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url, table_name="specializations_async") for url in urls]
        await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Async finished in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
