# Сравнение методов параллельного программирования в Python

В этом проекте рассматриваются три подхода к параллельному программированию на двух типах задач:

## Task 1: Вычисление суммы чисел от 1 до 100_000_000

1. **Асинхронный подход (`asyncio`)**
2. **Многопроцессный подход (`multiprocessing`)**
3. **Многопоточный подход (`threading`)**

## Task 2: Парсинг книг с веб-сайта и сохранение в PostgreSQL

1. **Асинхронный подход (`aiohttp`)**
2. **Многопроцессный подход (`ProcessPoolExecutor`)**
3. **Многопоточный подход (`ThreadPoolExecutor`)**

---

## Task 1: Сравнение методов вычисления суммы чисел

### 1. Асинхронный подход

```python
import asyncio
import time

TOTAL = 100_000_000
NUM_WORKERS = 4

async def calculate_sum(start, end):
    return await asyncio.to_thread(sum, range(start, end + 1))

async def main():
    step = TOTAL // NUM_WORKERS
    tasks = []

    start_time = time.time()

    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else TOTAL
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)

    total = sum(results)
    duration = time.time() - start_time

    print(f"Async total sum: {total}")
    print(f"Async duration: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

**Особенности:**
- Использует `asyncio` и корутины
- Эффективно при работе с I/O, но не даёт прироста на CPU-bound задачах
- Использует `asyncio.to_thread()` для выполнения CPU-интенсивных операций

**Результат:** 1.12 секунд


### 2. Многопроцессный подход

```python
from multiprocessing import Process, Array
import time
import os

TOTAL = 100_000_000
NUM_WORKERS = os.cpu_count() or 4

def calculate_sum(start, end, index, results):
    results[index] = sum(range(start, end + 1))

def main():
    step = TOTAL // NUM_WORKERS
    results = Array('Q', NUM_WORKERS)
    processes = []

    start_time = time.time()

    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else TOTAL
        p = Process(target=calculate_sum, args=(start, end, i, results))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(results)
    duration = time.time() - start_time

    print(f"Multiprocessing total sum: {total}")
    print(f"Multiprocessing duration: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
```

**Особенности:**
- Создаёт отдельные процессы для каждой части задачи
- Хорошо масштабируется на CPU-bound задачах
- Использует `Array` для разделяемой памяти между процессами
- Автоматически определяет количество ядер процессора

**Результат:** 0.24 секунды ⚡ **(самый быстрый!)**



### 3. Многопоточный подход

```python
import threading
import time

TOTAL = 100_000_000
NUM_WORKERS = 4
results = [0] * NUM_WORKERS

def calculate_sum(start, end, index):
    results[index] = sum(range(start, end + 1))

def main():
    step = TOTAL // NUM_WORKERS
    threads = []

    start_time = time.time()

    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else TOTAL
        thread = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)
    duration = time.time() - start_time

    print(f"Threading total sum: {total}")
    print(f"Threading duration: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
```

**Особенности:**
- Использует потоки в одном процессе
- Подходит для I/O-bound задач
- На CPU-bound задачах выигрыша нет из-за GIL (Global Interpreter Lock)
- Использует глобальный список для хранения результатов

**Результат:** 1.20 секунд

---

## Task 2: Парсинг книг с веб-сайта и сохранение в PostgreSQL

### 1. Асинхронный подход

```python
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from db import AsyncSessionLocal, async_init_db
from models import Book, Genres

BASE_URL = "https://books.toscrape.com/catalogue/category/books_1/index.html"

async def fetch_books_async():
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            books = []
            for book_tag in soup.select(".product_pod"):
                title = book_tag.select_one("h3 a")["title"]
                author_tag = book_tag.select_one(".author")
                author = author_tag.text.strip() if author_tag else "Unknown"
                genre_enum = Genres.non_fi
                published_year = 2025
                books.append(Book(
                    title=title,
                    author=author,
                    genre=genre_enum,
                    published_year=published_year
                ))
            return books

async def save_books_async(books):
    if not books:
        return
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for book in books:
                session.add(book)

async def main():
    await async_init_db()
    books = await fetch_books_async()
    await save_books_async(books)
    print(f"Добавлено книг: {len(books)}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Результат:** 20 книг

### 2. Многопоточный подход

```python
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from db import engine, init_db
from models import Book, Genres

def fetch_books_sync():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    books = []
    for book_tag in soup.select(".product_pod"):
        title = book_tag.select_one("h3 a")["title"]
        author_tag = book_tag.select_one(".author")
        author = author_tag.text.strip() if author_tag else "Unknown"
        genre_enum = Genres.non_fi
        published_year = 2025
        books.append(Book(title=title, author=author, genre=genre_enum, published_year=published_year))
    return books

def run_threading():
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_books_sync) for _ in range(5)]
        all_books = []
        for f in futures:
            all_books.extend(f.result())
        save_books(all_books)
        print(f"Добавлено книг (threading): {len(all_books)}")
```

**Результат:** 100 книг (5 потоков × 20 книг)

### 3. Многопроцессный подход

```python
from concurrent.futures import ProcessPoolExecutor
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from db import engine, init_db
from models import Book, Genres

def fetch_books_sync(_=None):
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    books = []
    for book_tag in soup.select(".product_pod"):
        title = book_tag.select_one("h3 a")["title"]
        author_tag = book_tag.select_one(".author")
        author = author_tag.text.strip() if author_tag else "Unknown"
        genre_enum = Genres.non_fi
        published_year = 2025
        books.append(Book(title=title, author=author, genre=genre_enum, published_year=published_year))
    return books

def run_multiprocessing():
    with ProcessPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_books_sync, range(5))
        all_books = []
        for r in results:
            all_books.extend(r)
        save_books(all_books)
        print(f"Добавлено книг (multiprocessing): {len(all_books)}")
```

**Результат:** 100 книг (5 процессов × 20 книг)

---

## Выводы

### Task 1 - CPU-интенсивные задачи:
- **Многопроцессный подход** показал лучшую производительность (0.24 сек)
- **Асинхронный подход** - 1.12 сек
- **Многопоточный подход** - 1.20 сек

### Task 2 - I/O-интенсивные задачи:
- Все подходы работают эффективно для веб-парсинга
- **Асинхронный подход** - 20 книг (один запрос)
- **Многопоточный и многопроцессный подходы** - 100 книг (5 параллельных запросов)

### Общие рекомендации:
- **Для CPU-bound задач** эффективнее использовать `multiprocessing`
- **Для I/O-bound задач** подойдут `asyncio` или `threading`
- **Многопроцессность** даёт максимальный прирост производительности на CPU-интенсивных операциях
- **GIL (Global Interpreter Lock)** ограничивает эффективность многопоточности в Python для CPU-задач

### Технические детали:
- Использована база данных PostgreSQL
- Применены современные библиотеки: `aiohttp`, `SQLModel`, `BeautifulSoup`
- Все методы дают корректный результат: 5000000050000000


