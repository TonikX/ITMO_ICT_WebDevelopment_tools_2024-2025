import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from task2.config import SITES
from task2.database import Task, get_session, clear_tasks

async def parse_and_save(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.title.string.strip() if soup.title else "No title"
                with get_session() as db_session:
                    existing = db_session.query(Task).filter(Task.description == url).first()
                    if not existing:
                        task = Task(title=title, description=url, user_id=1)
                        db_session.add(task)
                        db_session.commit()
                        print(f"[Async] Сохранено: {url} -> {title}")
                    else:
                        print(f"[Async] Пропущено (уже существует): {url}")
    except aiohttp.ClientError as e:
        print(f"[Async] Ошибка при запросе {url}: {e}")

async def main():
    tasks = [parse_and_save(url) for url in SITES]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import sys
    sys.path.append('/Users/user/Desktop/time_manager_app')
    clear_tasks()
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"[Async] Время: {end - start:.2f} секунд")