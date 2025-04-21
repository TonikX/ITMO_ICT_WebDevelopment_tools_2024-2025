import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from typing import List
from db_utils import init_db, save_page

async def parse_and_save(url: str, session) -> None:
    """Парсит веб-страницу и сохраняет её в базу данных асинхронно."""
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string if soup.title else "Заголовок не найден"
                
                # Сохранение в базу данных
                save_page(session, url, title)
                print(f"Успешно распарсено и сохранено: {url}")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")

async def parse_urls(urls: List[str]) -> None:
    """Парсит несколько URL с использованием асинхронности."""
    session = init_db()
    tasks = []
    
    for url in urls:
        task = asyncio.create_task(parse_and_save(url, session))
        tasks.append(task)
    
    await asyncio.gather(*tasks)

async def main():
    # Примеры URL для парсинга
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.reddit.com",
        "https://www.wikipedia.org"
    ]
    
    start_time = time.time()
    await parse_urls(urls)
    end_time = time.time()
    
    print(f"\async завершен за {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    asyncio.run(main()) 