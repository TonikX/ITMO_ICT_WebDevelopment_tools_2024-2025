import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
import sqlite3


async def parse_and_save(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            content = await response.read()
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else f"Без заголовка - {url}"

            conn = sqlite3.connect('pages.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO pages (url, title) VALUES (?, ?)', (url, title))
            conn.commit()
            conn.close()

            print(f"Сохранено: {title}")
    except Exception as e:
        print(f"Ошибка для {url}: {e}")


async def main():
    conn = sqlite3.connect('pages.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pages 
                     (id INTEGER PRIMARY KEY, url TEXT, title TEXT)''')
    conn.commit()
    conn.close()

    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://jsonplaceholder.typicode.com/',
        'https://httpbin.org/status/200',
        'https://httpbin.org/headers',
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/delay/1'
    ]

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Количество задач: {len(urls)}")


if __name__ == "__main__":
    asyncio.run(main())