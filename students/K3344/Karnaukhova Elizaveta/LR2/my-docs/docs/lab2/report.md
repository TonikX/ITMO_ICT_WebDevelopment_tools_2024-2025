# Отчет по лабораторной работе 2

## Введение
Цель работы: понять отличия потоками и процессами и понять, что такое ассинхронность в Python.

## Задача 1. Различия между threading, multiprocessing и async в Python
Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.
### threading
```python
import threading
import time


def calculate_sum(start, end, result, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def threading_sum(N, num_threads=4):
    chunk_size = N // num_threads
    threads = []
    result = [0] * num_threads

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else N
        thread = threading.Thread(target=calculate_sum, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(result)

    end_time = time.time()
    print(f"Threading sum: {total}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    N = 1_000_000_000
    threading_sum(N)

# first tray Threading sum: 500000000500000000
# Time taken: 28.3993 seconds

# second tray Threading sum: 500000000500000000
# Time taken: 29.0507 seconds
```
Использует модуль threading для создания потоков

Из-за Global Interpreter Lock (GIL) в Python потоки выполняются псевдопараллельно

Время выполнения: ~28-29 секунд
### multiprocessing
```python
import multiprocessing
import time


def calculate_sum(start, end, result, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def multiprocessing_sum(N, num_processes=4):
    chunk_size = N // num_processes  # Разбиваем N на части
    processes = []
    manager = multiprocessing.Manager()
    results = manager.list([0] * num_processes)

    start_time = time.time()

    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_processes - 1 else N
        # Создаем процесс для каждой части
        process = multiprocessing.Process(target=calculate_sum, args=(start, end, results, i))
        processes.append(process)
        process.start()  # Запускаем процессы параллельно

    for process in processes:
        process.join()  # Ожидаем завершения всех процессов

    total = sum(results)

    end_time = time.time()
    print(f"Multiprocessing sum: {total}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    N = 1_000_000_000
    multiprocessing_sum(N)

# first tray Multiprocessing sum: 500000000500000000
# Time taken: 9.7730 seconds

# second tray Multiprocessing sum: 500000000500000000
# Time taken: 9.4755 seconds

```
Использует модуль multiprocessing для создания отдельных процессов

Каждый процесс имеет свой собственный интерпретатор Python и память

Время выполнения: ~9-10 секунд (в 3 раза быстрее threading)
### async
```python
import asyncio
import time


async def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def async_sum(N, num_tasks=4):
    chunk_size = N // num_tasks
    tasks = []

    start_time = time.time()

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else N
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)
    total = sum(results)

    end_time = time.time()
    print(f"Async sum: {total}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    N = 1_000_000_000
    asyncio.run(async_sum(N))

# first tray Async sum: 500000000500000000
# Time taken: 29.7306 seconds

# second tray Async sum: 500000000500000000
# Time taken: 28.7105 seconds

```
Использует асинхронное программирование с asyncio

Не создает дополнительные потоки или процессы, а использует кооперативную многозадачность

Время выполнения: ~28-30 секунд (аналогично threading)

### Выводы
Результаты времени выполнения

| Подход          | Время выполнения (сек) | Примечания                         |
|-----------------|------------------------|------------------------------------|
| Threading       | 28.40 - 29.05          | GIL мешает параллельности          |
| Multiprocessing | 9.47 - 9.77            | Лучший вариант для CPU-bound задач |
| Async           | 28.71 - 29.73          | Не дает преимуществ для вычислений |
Multiprocessing значительно быстрее, так как обходит GIL.

Threading и Async работают медленно из-за ограничений GIL.

Для CPU-интенсивных задач (как вычисление суммы):

Multiprocessing показывает наилучшие результаты, так как обходит GIL за счет использования отдельных процессов

Threading и Async работают примерно одинаково медленно, так как GIL блокирует параллельное выполнение Python-кода

Async не дает преимуществ для CPU-задач, так как предназначен для I/O-операций
## Задача 2. Параллельный парсинг веб-страниц с сохранением в базу данных
Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.
### threading
```python
import random
import threading
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from sqlmodel import select
from models import *
from threading import Lock

DATABASE_URL = "postgresql://postgres:992327@localhost:8000/book_db"
# Создаем engine для каждого потока отдельно
engine = None
db_lock = Lock()  # Блокировка для работы с БД
SQLModel.metadata.create_all(create_engine(DATABASE_URL))

URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


def get_engine():
    """Создаем новый engine для каждого потока"""
    return create_engine(DATABASE_URL)


def parse_books(url: str) -> List[BookItem]:
    """Парсинг книг со страницы автора"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        author = soup.find('div', class_='author-header__name').text.strip()

        books = []
        for book_item in soup.find_all('div', class_='book-item__inner'):
            title = book_item.find('a', class_='book-item__title').text.strip()
            description = book_item.find('p')
            description = ".".join(description.text.strip().split(".")[:3]) + "." if description else None

            books.append(BookItem(
                title=title,
                author=author,
                description=description
            ))
        return books
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")
        return []


def save_books(books: List[BookItem]):
    """Сохранение книг в БД с блокировкой"""
    global engine
    if not books:
        return

    with db_lock:
        try:
            # Создаем engine при первом использовании в потоке
            if engine is None:
                engine = get_engine()

            with Session(engine) as session:
                # Получаем список всех пользователей
                users = session.exec(select(UserProfile)).all()
                if not users:
                    print("Нет пользователей в базе данных. Сначала создайте пользователей.")
                    return

                for book in books:
                    # Создаем книгу
                    session.add(book)
                    session.commit()
                    session.refresh(book)

                    # Связываем книгу со случайным пользователем
                    random_user = random.choice(users)
                    user_book = UserBook(
                        user_profile_id=random_user.id,
                        book_item_id=book.id,
                        status=BookStatus.AVAILABLE
                    )
                    session.add(user_book)

                session.commit()
        except Exception as e:
            print(f"Ошибка при сохранении книг: {str(e)}")


def parse_and_save(url: str):
    """Функция для потока: парсинг и сохранение"""
    print(f"Начало парсинга {url}")
    try:
        books = parse_books(url)
        if books:
            save_books(books)
            print(f"Успешно сохранено {len(books)} книг с {url}")
        else:
            print(f"Не удалось получить книги с {url}")
    except Exception as e:
        print(f"Ошибка в потоке для {url}: {str(e)}")


def main():
    start_time = time.time()

    threads = []
    for url in URLS:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    main()

# Начало парсинга https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Начало парсинга https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Начало парсинга https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Успешно сохранено 20 книг с https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Успешно сохранено 20 книг с https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Успешно сохранено 20 книг с https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Общее время выполнения: 0.52 секунд
```
Использует потоки для параллельного парсинга
Потоки эффективны для I/O, так как GIL освобождается во время ожидания.
### multiprocessing
```python
import multiprocessing
from multiprocessing import Pool
import random
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from sqlmodel import select
from models import *

DATABASE_URL = "postgresql://postgres:992327@localhost:8000/book_db"


def get_engine():
    """Создаем новый engine для каждого процесса"""
    return create_engine(DATABASE_URL)


URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


def parse_books(url: str) -> List[BookItem]:
    """Парсинг книг со страницы автора"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    author = soup.find('div', class_='author-header__name').text.strip()

    books = []
    for book_item in soup.find_all('div', class_='book-item__inner'):
        title = book_item.find('a', class_='book-item__title').text.strip()
        description = book_item.find('p')
        description = ".".join(description.text.strip().split(".")[:3]) + "." if description else None

        books.append(BookItem(
            title=title,
            author=author,
            description=description
        ))

    return books


def save_books(books: List[BookItem], engine):
    """Сохранение книг в БД"""
    with Session(engine) as session:
        # Получаем список всех пользователей
        users = session.exec(select(UserProfile)).all()
        if not users:
            print("Нет пользователей в базе данных. Сначала создайте пользователей.")
            return

        for book in books:
            # Создаем книгу
            session.add(book)
            session.commit()
            session.refresh(book)

            # Связываем книгу со случайным пользователем
            random_user = random.choice(users)
            user_book = UserBook(
                user_profile_id=random_user.id,
                book_item_id=book.id,
                status=BookStatus.AVAILABLE
            )
            session.add(user_book)

        session.commit()


def parse_and_save(url: str):
    """Функция для процесса: парсинг и сохранение"""
    print(f"Парсинг {url}")
    try:
        # Создаем engine внутри процесса
        engine = get_engine()
        books = parse_books(url)
        save_books(books, engine)
        print(f"Сохранено {len(books)} книг с {url}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {str(e)}")


def main():
    start_time = time.time()

    # Создаем таблицы в основном процессе
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

    # Запускаем процессы
    with Pool(processes=min(len(URLS), multiprocessing.cpu_count())) as pool:
        pool.map(parse_and_save, URLS)

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

# Парсинг https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Парсинг https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Парсинг https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Сохранено 20 книг с https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Сохранено 20 книг с https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Сохранено 20 книг с https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Общее время выполнения: 1.26 секунд

```
Использует отдельные процессы через Pool
Избыточен для I/O-задач, так как создает дополнительные процессы.
### async
```python
import asyncio
import random
from sqlmodel import select

import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session, create_engine
import time
from models import *

DATABASE_URL = "postgresql://postgres:992327@localhost:8000/book_db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

URLS = [
    "https://www.livelib.ru/author/162944/latest-brendon-sanderson",
    "https://www.livelib.ru/author/518692/latest-fredrik-bakman",
    "https://www.livelib.ru/author/357494/latest-sara-dzh-maas"
]


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def parse_books(url: str) -> List[BookItem]:
    """Асинхронный парсинг книг"""
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        author = soup.find('div', class_='author-header__name').text.strip()

        books = []
        for book_item in soup.find_all('div', class_='book-item__inner'):
            title = book_item.find('a', class_='book-item__title').text.strip()
            description = book_item.find('p')
            description = ".".join(description.text.strip().split(".")[:3]) + "." if description else None

            books.append(BookItem(
                title=title,
                author=author,
                description=description
            ))

        return books


async def save_books(books: List[BookItem]):
    """Асинхронное сохранение книг"""
    with Session(engine) as session:
        # Получаем список всех пользователей
        users = session.exec(select(UserProfile)).all()
        if not users:
            print("Нет пользователей в базе данных. Сначала создайте пользователей.")
            return

        for book in books:
            # Создаем книгу
            session.add(book)
            session.commit()
            session.refresh(book)

            # Связываем книгу со случайным пользователем
            random_user = random.choice(users)
            user_book = UserBook(
                user_profile_id=random_user.id,
                book_item_id=book.id,
                status=BookStatus.AVAILABLE
            )
            session.add(user_book)

        session.commit()


async def parse_and_save(url: str):
    """Асинхронная задача"""
    print(f"Парсинг {url}")
    books = await parse_books(url)
    await save_books(books)
    print(f"Сохранено {len(books)} книг с {url}")


async def main():
    start_time = time.time()

    tasks = [parse_and_save(url) for url in URLS]
    await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    asyncio.run(main())

# Парсинг https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Парсинг https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Парсинг https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Сохранено 20 книг с https://www.livelib.ru/author/357494/latest-sara-dzh-maas
# Сохранено 20 книг с https://www.livelib.ru/author/518692/latest-fredrik-bakman
# Сохранено 20 книг с https://www.livelib.ru/author/162944/latest-brendon-sanderson
# Общее время выполнения: 0.54 секунд
```
Использует асинхронные HTTP-запросы через aiohttp
Оптимален для I/O, так как использует неблокирующие запросы.

### Выводы
Результаты времени выполнения

| Подход          | Время выполнения (сек) | Примечания                           |
|-----------------|------------------------|--------------------------------------|
| Threading       | 0.52                   | Хорошо подходит для I/O              |
| Multiprocessing | 1.26                   | Избыточные накладные расходы         |
| Async           | 0.54                   | Лучший вариант для асинхронных задач |

Threading и Async показывают схожую скорость, так как GIL не блокирует I/O.

Multiprocessing медленнее из-за накладных расходов на процессы.

**Анализ результатов**

Для I/O-интенсивных задач (как парсинг веб-страниц):

Threading и Async показывают схожие и лучшие результаты, так как GIL освобождается во время I/O-операций

Multiprocessing оказывается медленнее из-за накладных расходов на создание процессов

Async демонстрирует чистый и эффективный код для подобных задач

## Общие выводы
**Для CPU-интенсивных задач:**

Лучший выбор: Multiprocessing (истинный параллелизм)

Threading и Async не дают преимуществ из-за GIL

**Для I/O-интенсивных задач:**

Лучшие выбор: Threading или Async

Async предпочтительнее из-за более чистого кода и отсутствия проблем с синхронизацией

Multiprocessing избыточен и создает дополнительные накладные расходы

**Общие рекомендации:**

Используйте multiprocessing для тяжелых вычислений

Используйте async для I/O-операций (сетевые запросы, работа с БД)

Threading может быть полезен для простых I/O-задач, но имеет проблемы с синхронизацией

### Практическая применимость подходов
**Threading (многопоточность)**

**Где применять:**

I/O-bound задачи с блокирующими вызовами (запросы к API, чтение/запись файлов, работа с БД)

GUI-приложения (чтобы не блокировать интерфейс)

Простая параллельная обработка, где не требуется высокая производительность

**Ограничения:**

Бесполезен для CPU-bound задач из-за GIL

Проблемы с race conditions (нужны блокировки)

Нет реального параллелизма (только псевдопараллельное выполнение)

**Multiprocessing (многопроцессорность)**

**Где применять:**

CPU-intensive задачи (машинное обучение, сложные вычисления)

Обработка больших данных (Pandas, NumPy)

Изолированные задачи, где нужна стабильность (крах процесса не убьет всю программу)

**Ограничения:**

Высокий overhead (затраты на создание процессов)

Сложный обмен данными (нужны Queue, Pipe, shared memory)

Потребляет много памяти (каждый процесс — отдельный интерпретатор Python)

**Async (асинхронность)**

**Где применять:**

Высоконагруженные I/O-приложения (веб-серверы, чат-боты)

Микросервисная архитектура (множество внешних вызовов)

Реалтайм-системы (WebSockets, long-polling)

**Ограничения:**

Требует специальных библиотек (aiohttp вместо requests, asyncpg вместо psycopg2)

Вся цепочка вызовов должна быть async ("async infection")

Сложная отладка (stack traces с корутинами)