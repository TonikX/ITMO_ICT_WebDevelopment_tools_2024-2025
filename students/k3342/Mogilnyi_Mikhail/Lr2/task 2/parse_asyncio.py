import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from saver import save_title_to_category
from db import get_session

BASE_URLS = [
    "https://rusbid.de/shops/food",
    "https://rusbid.de/shops/sports",
    "https://rusbid.de/shops/electronics"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}


async def fetch(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', class_='btn-panel')
            titles = [link.text.strip() for link in links if link.text.strip()]
            print(f"🔍 Найдено {len(titles)} категорий с {url}")
            return titles
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")
        return []


async def main():
    start_time = time.time()

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [fetch(session, url) for url in BASE_URLS]
        results = await asyncio.gather(*tasks)

    all_titles = [title for sublist in results for title in sublist]

    for session in get_session():
        for title in all_titles:
            save_title_to_category(title, session)

    end_time = time.time()
    print(f"Завершено за {end_time - start_time:.2f} сек.")

if __name__ == "__main__":
    asyncio.run(main())
