
import asyncio
import sqlite3
import threading
import time
import aiohttp
import aiosqlite
from bs4 import BeautifulSoup
import multiprocessing
import uuid
import requests


def init_db():
    conn = sqlite3.connect('web_pages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT
        )
    ''')
    conn.commit()
    conn.close()

URLS = [
    'https://example.com',
    'https://python.org',
    'https://wikipedia.org',
    'https://github.com'
    'https://stackoverflow.com',
    'https://www.reddit.com',
    'https://www.quora.com',
    'https://www.pinterest.com',
    'https://vk.com',
]

def parse_and_save_threading(url, results, index):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'

        conn = sqlite3.connect('web_pages.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pages (id, url, title) VALUES (?, ?, ?)',
                       (str(uuid.uuid4()), url, title))
        conn.commit()
        conn.close()

        results[index] = f"Parsed {url}: {title}"
    except Exception as e:
        results[index] = f"Error parsing {url}: {str(e)}"

def run_threading_parsing():
    start_time = time.time()
    threads = []
    results = [None] * len(URLS)

    for i, url in enumerate(URLS):
        thread = threading.Thread(target=parse_and_save_threading, args=(url, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed_time = time.time() - start_time
    return results, elapsed_time

def parse_and_save_multiprocessing(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'

        conn = sqlite3.connect('web_pages.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pages (id, url, title) VALUES (?, ?, ?)',
                       (str(uuid.uuid4()), url, title))
        conn.commit()
        conn.close()

        return f"Parsed {url}: {title}"
    except Exception as e:
        return f"Error parsing {url}: {str(e)}"

def run_multiprocessing_parsing():
    start_time = time.time()
    pool = multiprocessing.Pool(processes=len(URLS))
    results = pool.map(parse_and_save_multiprocessing, URLS)
    pool.close()
    pool.join()
    elapsed_time = time.time() - start_time
    return results, elapsed_time

async def parse_and_save_async(url, session):
    try:
        async with session.get(url, timeout=5) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            title = soup.title.string if soup.title else 'No title'

            async with aiosqlite.connect('web_pages.db') as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('INSERT INTO pages (id, url, title) VALUES (?, ?, ?)',
                                         (str(uuid.uuid4()), url, title))
                    await conn.commit()

            return f"Parsed {url}: {title}"
    except Exception as e:
        return f"Error parsing {url}: {str(e)}"

async def run_async_parsing():
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save_async(url, session) for url in URLS]
        results = await asyncio.gather(*tasks)
    elapsed_time = time.time() - start_time
    return results, elapsed_time



def generate_documentation(threading_time, multiprocessing_time, async_time):
    doc = f"""
## Задача 2: Парсинг веб-страниц

### Подход с потоками (Threading)
- **Описание**: Использует `threading` для одновременного парсинга нескольких веб-страниц и сохранения заголовков в базу данных SQLite.
- **Реализация**: Каждому URL назначается поток, используется `requests` и `BeautifulSoup` для парсинга.
- **Особенности**:
  - Подходит для задач с вводом-выводом, но ограничен GIL при нагрузке на процессор.
  - Прост в реализации, но возможны конфликты при одновременном доступе к базе данных.
- **Время выполнения**: {threading_time:.2f} секунд

### Подход с многопроцессностью (Multiprocessing)
- **Описание**: Использует `multiprocessing` для парсинга веб-страниц в отдельных процессах.
- **Реализация**: Распределяет URL между процессами через пул, каждый процесс выполняет парсинг и сохраняет данные в базу.
- **Особенности**:
  - Обеспечивает настоящий параллелизм, устраняя влияние GIL.
  - Более высокие накладные расходы из-за создания процессов, но эффективен при высоких нагрузках на CPU.
- **Время выполнения**: {multiprocessing_time:.2f} секунд

### Асинхронный подход (Async)
- **Описание**: Использует `aiohttp` и `asyncio` для асинхронных веб-запросов и парсинга.
- **Реализация**: Создаёт асинхронные задачи для каждого URL, использует единый `ClientSession` для повышения эффективности.
- **Особенности**:
  - Высокая эффективность для задач с вводом-выводом, таких как веб-запросы.
  - Избегает блокировок и максимально использует ресурсы за счёт event loop.
- **Время выполнения**: {async_time:.2f} секунд

## Сравнение производительности

| Подход          | Время выполнения (секунды) |
|------------------|----------------------------|
| Threading        | {threading_time:.2f}       |
| Multiprocessing  | {multiprocessing_time:.2f} |
| Async            | {async_time:.2f}           |

## Заключение
- **Async** обычно самый быстрый для задач с вводом-выводом, таких как веб-запросы, благодаря неблокирующему I/O и эффективному управлению через event loop.
- **Threading** показывает хорошие результаты, но может замедляться из-за GIL и конкуренции потоков при записи в базу данных.
- **Multiprocessing** работает медленнее из-за накладных расходов на создание процессов и межпроцессное взаимодействие, что снижает его эффективность в задачах с вводом-выводом.
"""
    return doc

# Main execution
if __name__ == "__main__":
    # Initialize database
    init_db()

    # Task 2
    print("\nTask 2: Web Parsing")
    threading_results, threading_time = run_threading_parsing()
    print("Threading Results:")
    for res in threading_results:
        print(res)
    print(f"Time = {threading_time:.2f} seconds")

    multiprocessing_results, multiprocessing_time = run_multiprocessing_parsing()
    print("Multiprocessing Results:")
    for res in multiprocessing_results:
        print(res)
    print(f"Time = {multiprocessing_time:.2f} seconds")

    async_results, async_time = asyncio.run(run_async_parsing())
    print("Async Results:")
    for res in async_results:
        print(res)
    print(f"Time = {async_time:.2f} seconds")

    # Generate and print documentation
    doc = generate_documentation(threading_time, multiprocessing_time, async_time)
    with open("lab2_report_scraping.md", "w") as f:
        f.write(doc)

    print("Documentation generated: lab2_report_scraping.md")
    print("Web pages parsed and stored in database.")
