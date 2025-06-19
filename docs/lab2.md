# Параллельные вычисления и веб-парсинг в Python

## Оглавление
- [Параллельные вычисления и веб-парсинг в Python](#параллельные-вычисления-и-веб-парсинг-в-python)
  - [Оглавление](#оглавление)
  - [Задача 1: threading, multiprocessing и async](#задача-1-threading-multiprocessing-и-async)
    - [Threading](#threading)
    - [Async](#async)
    - [Multiprocessing](#multiprocessing)
  - [Задание 2:](#задание-2)
    - [Async:](#async-1)
    - [Multipricessing:](#multipricessing)
    - [Threading:](#threading-1)

---

## Задача 1: threading, multiprocessing и async

### Threading
```python
import threading
import time

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))

def main():
    total = 1000_000_000
    threads_num = 4
    chunk_size = total // threads_num
    results = [0] * threads_num
    threads = []

    start_time = time.time()

    for i in range(threads_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != threads_num - 1 else total
        thread = threading.Thread(
            target=calculate_sum,
            args=(start, end, results, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Threading sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
```
### Async
```python
import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    total = 1000_000_000
    tasks_num = 4
    chunk_size = total // tasks_num
    tasks = []

    start_time = time.time()

    for i in range(tasks_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != tasks_num - 1 else total
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    end_time = time.time()

    print(f"Async sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```
### Multiprocessing

```python
from multiprocessing import Process, Manager
import time

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))

def main():
    total = 1000_000_000
    processes_num = 4
    chunk_size = total // processes_num

    with Manager() as manager:
        results = manager.list([0] * processes_num)
        processes = []

        start_time = time.time()

        for i in range(processes_num):
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size if i != processes_num - 1 else total
            process = Process(
                target=calculate_sum,
                args=(start, end, results, i))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        total_sum = sum(results)
        end_time = time.time()

    print(f"Multiprocessing sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
```

## Задание 2:
```
urls = [
    "https://xmas-hack.ru",
    "https://en.wikipedia.org/wiki/Hackathon",
    "https://www.python.org",
    "https://wikipedia.org/wiki/Hackathon",
    "https://www.kaggle.com/events",
    "https://techcrunch.com/startups/",
]
```

### Async:
```python
import asyncio
import time
import aiohttp
import ssl
import certifi
from bs4 import BeautifulSoup
from sqlmodel import Session, SQLModel
from connection import engine
from lr2.task2.urls import urls
from models import Page

async def parse_and_save(url, session):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"HTTP Error {response.status} for {url}")
                return

            html = await response.text()
            bs = BeautifulSoup(html, "html.parser")

            title = None
            if bs.title and bs.title.string:
                title = bs.title.string.strip()
            elif bs.find("h1"):
                title = bs.find("h1").text.strip()

            with Session(engine) as db:
                page = Page(url=url, title=title)
                db.add(page)
                db.commit()
                print(f"Success: {url} | Title: {title if title else 'No title found'}")

    except Exception as e:
        print(f"Error parsing {url}: {str(e)}")

async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=10,
        force_close=True,
        enable_cleanup_closed=True
    )

    start = time.time()

    async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=15)
    ) as session:
        tasks = [parse_and_save(url, session) for url in urls]
        await asyncio.gather(*tasks)

    end = time.time()
    print(f"\nAsync time: {end - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
```
```
 Async time: 0.70 seconds
```

### Multipricessing:
```python
from multiprocessing import Pool
import time
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from connection import engine
from models import Page
from lr2.task2.urls import urls

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        bs = BeautifulSoup(response.text, "html.parser")
        title = bs.title.string if bs.title else None

        with Session(engine) as db:
            page = Page(url=url, title=title)
            db.add(page)
            db.commit()
            print(f"Parsed: {url} | Title: {title}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")

def main():
    start = time.time()
    with Pool(4) as pool:
        pool.map(parse_and_save, urls)

    end = time.time()
    print(f"\nMultiprocessing time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()
```

```
 Multiprocessing time: 1.61 seconds
```
### Threading:

```python
import threading
import time
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, SQLModel
from connection import engine
from lr2.task2.urls import urls
from models import Page

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        bs = BeautifulSoup(response.text, "html.parser")
        title = bs.title.string if bs.title else None

        with Session(engine) as db:
            page = Page(url=url, title=title)
            db.add(page)
            db.commit()
            print(f"Parsed: {url} | Title: {title}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")

def main():
    threads = []

    start = time.time()
    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end = time.time()
    print(f"\nThreading time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()
```

```
 Threading time: 0.90 seconds
```
