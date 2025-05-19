# Лабораторная работа №2 Потоки. Процессы. Асинхронность.

## Задача 1. Различия между threading, multiprocessing и async в Python

### Описание задачи

Целью данной задачи было изучение и демонстрация различий между тремя основными подходами к параллельным вычислениям в Python: **`threading`**, **`multiprocessing`** и **`asyncio`**. Для этого были разработаны три отдельные программы, каждая из которых использовала один из указанных подходов для решения вычислительно-интенсивной задачи: подсчета суммы всех чисел от 1 до 1 000 000 000. Вычисления были разделены на несколько параллельных подзадач для ускорения выполнения.

### Используемые подходы и их особенности

---

### Threading (Многопоточность)

**Описание:** Модуль `threading` позволяет создавать и управлять потоками (threads) внутри одного процесса. Потоки используют одно и то же адресное пространство памяти, что упрощает обмен данными между ними. Однако, из-за наличия **Global Interpreter Lock (GIL)** в CPython, истинный параллелизм для CPU-bound задач (таких как вычисления) не достигается, так как в любой момент времени только один поток может выполнять Python-байткод. `threading` более эффективен для **I/O-bound** задач, где потоки ожидают ввода/вывода, освобождая GIL для других потоков.

**Реализация:**
В программе `threading_sum.py` задача подсчета суммы чисел была разделена на 4 подзадачи, каждая из которых выполнялась отдельным потоком. Результаты каждой подзадачи сохранялись в общий список.

**Код**:  
```python
import threading
import time

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end))

if __name__ == "__main__":
    start_time = time.time()
    total = 1_000_000_000
    num_threads = 4
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        start = i * step + 1
        end = start + step
        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Total sum: {sum(results)}")
    print(f"Execution time (threading): {time.time() - start_time:.2f} seconds")
```

---

### Multiprocessing (Многопроцессорность)

**Описание:** Модуль `multiprocessing` позволяет создавать и управлять отдельными процессами (processes). Каждый процесс имеет свое собственное адресное пространство памяти, что означает отсутствие GIL. Это позволяет достичь **истинного параллелизма** для CPU-bound задач, используя все доступные ядра процессора. Обмен данными между процессами требует явных механизмов, таких как очереди (`Queue`) или каналы (`Pipe`).

**Реализация:**
В программе `multiprocessing_sum.py` задача подсчета суммы чисел также была разделена на 4 подзадачи, но каждая из них выполнялась отдельным процессом. Для сбора результатов из каждого процесса использовалась очередь `multiprocessing.Queue`.

**Код**:
```python
import multiprocessing
import time

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end)))

if __name__ == "__main__":
    start_time = time.time()
    total = 1_000_000_000
    num_processes = 4
    step = total // num_processes
    processes = []
    queue = multiprocessing.Queue()

    for i in range(num_processes):
        start = i * step + 1
        end = start + step
        p = multiprocessing.Process(target=calculate_sum, args=(start, end, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    result = sum(queue.get() for _ in range(num_processes))
    print(f"Total sum: {result}")
    print(f"Execution time (multiprocessing): {time.time() - start_time:.2f} seconds")
```
---

### Asyncio (Асинхронное программирование)

**Описание:** `asyncio` - это библиотека для написания конкурентного кода с использованием синтаксиса `async/await`. Он основан на однопоточном, однопроцессном подходе, где конкурентность достигается путем переключения между задачами (корутинами), когда одна из них ожидает выполнения I/O операции. `asyncio` **не предназначен** для параллельных CPU-bound вычислений, так как все задачи выполняются в одном потоке и используют один и тот же GIL. Если одна задача долго занимает процессор, она блокирует выполнение всех остальных асинхронных задач.

**Реализация:**
В программе `async_sum.py` задача подсчета суммы чисел была представлена как несколько асинхронных задач (корутин). Эти задачи запускались с помощью `asyncio.gather`. Несмотря на асинхронный подход, поскольку `sum(range(start, end))` является CPU-bound операцией, истинный параллелизм не был достигнут.

**Код**:
```python
import multiprocessing
import time

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end)))

if __name__ == "__main__":
    start_time = time.time()
    total = 1_000_000_000
    num_processes = 4
    step = total // num_processes
    processes = []
    queue = multiprocessing.Queue()

    for i in range(num_processes):
        start = i * step + 1
        end = start + step
        p = multiprocessing.Process(target=calculate_sum, args=(start, end, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    result = sum(queue.get() for _ in range(num_processes))
    print(f"Total sum: {result}")
    print(f"Execution time (multiprocessing): {time.time() - start_time:.2f} seconds")
```

### Результаты выполнения и сравнение (Задача 1)

Для каждой программы было замерено время выполнения на одних и тех же входных данных (подсчет суммы чисел от 1 до 1 000 000 000).

---

| Подход         | Время выполнения (секунды) |
| :------------- |:---------------------------|
| **Threading** | 11.78                      |
| **Multiprocessing** | 3.35                       |
| **Asyncio** | 11.94                      |

---

### Комментарии к результатам (Задача 1)

Результаты наглядно демонстрируют ключевые различия между подходами применительно к CPU-bound задачам:

1.  **Multiprocessing - самый быстрый:** `multiprocessing` показал значительно лучшее время выполнения (3.35 секунды) по сравнению с `threading` и `asyncio`. Это ожидаемо, так как `multiprocessing` создает отдельные процессы, обходя проблему GIL, и позволяет эффективно использовать несколько ядер процессора для параллельных вычислений.

2.  **Threading и Asyncio - сопоставимо медленные:** Время выполнения для `threading` (11.78 секунды) и `asyncio` (11.94 секунды) оказалось почти идентичным и значительно дольше, чем у `multiprocessing`. Это подтверждает, что для CPU-bound задач:
    * **`threading`** страдает от GIL, который не позволяет потокам выполнять Python-байткод по-настоящему параллельно.
    * **`asyncio`** не предназначен для параллельных вычислений в пределах одного процесса. Его сила заключается в эффективном управлении I/O операциями.

## Задача 2. Параллельный парсинг веб-страниц с сохранением в базу данных

### Описание задачи

Вторая задача была посвящена применению параллельных подходов (`threading`, `multiprocessing`, `asyncio`) к **I/O-bound** задаче — параллельному парсингу нескольких веб-страниц и сохранению извлеченных данных (заголовков страниц, которые были использованы для генерации имени пользователя) в базу данных. Целью было сравнение производительности каждого подхода в условиях, где основное время тратится на ожидание сетевых запросов и операций с базой данных.

### Ход выполнения

Для каждого из подходов были написаны отдельные программы: `threading_parser.py`, `multiprocessing_parser.py`, и `async_parser.py`.

1.  **Подключение к базе данных:** Была настроена поддержка как синхронных (`SyncSession`), так и асинхронных (`AsyncSessionLocal`) подключений к PostgreSQL базе данных с использованием `SQLModel` и `SQLAlchemy`.
2.  **Определение модели данных:** Была создана простая модель `User` для хранения информации, полученной из веб-страниц (username, name, hashed_password, registration_date).
3.  **Функция `parse_and_save(url)`:**
    * Для **`threading`** и **`multiprocessing`** использовался синхронный HTTP-клиент `requests` для загрузки HTML-страницы. Парсинг осуществлялся с помощью `BeautifulSoup`. Сохранение данных в базу данных выполнялось через синхронную сессию `SyncSession`.
    * Для **`asyncio`** использовался асинхронный HTTP-клиент `aiohttp` для загрузки страниц и асинхронная сессия `AsyncSessionLocal` для работы с базой данных.
    * Извлечение `username` и `name` производилось путем поиска по тексту страницы с использованием регулярных выражений, а `hashed_password` генерировался случайным образом.
4.  **Распределение задач:** Список из 10 URL-адресов GitHub-профилей был использован в качестве входных данных. Для `threading` и `multiprocessing` задачи были разделены на равные части и распределены между потоками/процессами. В `asyncio` все задачи запускались одновременно в цикле событий.
5.  **Измерение времени:** Время выполнения каждой программы замерялось с помощью `time.time()`.

**Код threading_parser.py**:
```python
import threading
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import hashlib
import re
from models import User
from db import SyncSession, init_sync_db

init_sync_db()


def generate_fake_password(username):
    return hashlib.sha256(f"fake{username}{random.randint(1, 1000)}".encode()).hexdigest()


def parse_and_save(url, suffix):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)
        base_username = username_match.group(1) if username_match else url.split('/')[-1]
        name = username_match.group(2) if username_match else "Unknown"

        with SyncSession() as session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=generate_fake_password(base_username),
                registration_date=datetime.now()
            )
            session.add(user)
            session.commit()
            print(f"Saved: {user.username}")
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


def main():
    urls = [
        "https://github.com/torvalds",
        "https://github.com/gaearon",
        "https://github.com/dhh",
        "https://github.com/mojombo",
        "https://github.com/fabpot",
        "https://github.com/defunkt",
        "https://github.com/mitsuhiko",
        "https://github.com/jashkenas",
        "https://github.com/rasbt",
        "https://github.com/zzzeek",
    ]

    suffix = "_thread"
    num_threads = 4
    chunk_size = (len(urls) + num_threads - 1) // num_threads

    start = time.time()

    threads = []
    for i in range(num_threads):
        chunk = urls[i * chunk_size: (i + 1) * chunk_size]
        t = threading.Thread(
            target=lambda urls: [parse_and_save(u, suffix) for u in urls],
            args=(chunk,)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Threading time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
```

**Код multiprocessing_parser.py**:
```python
import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import hashlib
import re
from models import User
from db import SyncSession, init_sync_db


def init_process():
    init_sync_db()


def parse_and_save(args):
    url, suffix = args
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)
        base_username = username_match.group(1) if username_match else url.split('/')[-1]
        name = username_match.group(2) if username_match else "Unknown"

        with SyncSession() as session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=hashlib.sha256(
                    f"fake{base_username}{random.randint(1, 1000)}".encode()
                ).hexdigest(),
                registration_date=datetime.now()
            )
            session.add(user)
            session.commit()
            print(f"Saved: {user.username}")
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


def main():
    urls = [
        "https://github.com/torvalds",
        "https://github.com/gaearon",
        "https://github.com/dhh",
        "https://github.com/mojombo",
        "https://github.com/fabpot",
        "https://github.com/defunkt",
        "https://github.com/mitsuhiko",
        "https://github.com/jashkenas",
        "https://github.com/rasbt",
        "https://github.com/zzzeek",
    ]

    suffix = "_mp"
    start = time.time()

    with multiprocessing.Pool(
            4,
            initializer=init_process
    ) as pool:
        pool.map(parse_and_save, [(url, suffix) for url in urls])

    print(f"Multiprocessing time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
```

**Код async_parser.py**:
```python
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from datetime import datetime
import random
import hashlib
import re
from models import User
from db import AsyncSessionLocal, init_async_db, async_engine


async def generate_fake_password(username):
    return hashlib.sha256(f"fake{username}{random.randint(1, 1000)}".encode()).hexdigest()


async def parse_and_save(session, url, suffix):
    try:
        async with session.get(url) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        page_text = soup.get_text()

        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)
        base_username = username_match.group(1) if username_match else url.split('/')[-1]
        name = username_match.group(2) if username_match else "Unknown"

        async with AsyncSessionLocal() as db_session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=await generate_fake_password(base_username),
                registration_date=datetime.now()
            )
            db_session.add(user)
            await db_session.commit()
            print(f"Saved: {user.username}")

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


async def main():
    await init_async_db()

    urls = [
        "https://github.com/torvalds",
        "https://github.com/gaearon",
        "https://github.com/dhh",
        "https://github.com/mojombo",
        "https://github.com/fabpot",
        "https://github.com/defunkt",
        "https://github.com/mitsuhiko",
        "https://github.com/jashkenas",
        "https://github.com/rasbt",
        "https://github.com/zzzeek",
    ]

    suffix = "_async"
    start = time.time()

    async with aiohttp.ClientSession() as http_session:
        tasks = [parse_and_save(http_session, url, suffix) for url in urls]
        await asyncio.gather(*tasks)

    print(f"Async time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
```

### Результаты выполнения и сравнение (Задача 2)

---

| Подход         | Время выполнения (секунды) |
| :------------- |:---------------------------|
| **Threading** | 2.81                       |
| **Multiprocessing** | 2.29                       |
| **Asyncio** | 0.70                       |

---

### Анализ результатов (Задача 2)

Результаты для I/O-bound задачи значительно отличаются от CPU-bound:

1.  **Asyncio - самый быстрый:** `asyncio` показал наилучшее время выполнения (0.7 секунды). Это подтверждает его эффективность для задач, где большая часть времени тратится на ожидание (сетевые запросы, операции с базой данных). Благодаря асинхронному вводу-выводу, `asyncio` может эффективно переключаться между задачами, пока одна из них ожидает ответа от сервера или базы данных, не блокируя выполнение других.

2.  **Multiprocessing - хороший результат, но не лучший:** `multiprocessing` занял второе место (2.29 секунды). Хотя он и смог распараллелить работу благодаря отдельным процессам, накладные расходы на создание процессов и межпроцессное взаимодействие оказались выше, чем у `asyncio`, который работает в рамках одного процесса. Тем не менее, это все еще значительно быстрее, чем однопоточное выполнение.

3.  **Threading - ожидаемо медленнее, чем Asyncio:** `threading` показал время выполнения 2.81 секунды. В данном случае, GIL не так сильно влияет на производительность, как в CPU-bound задачах, поскольку потоки большую часть времени находятся в состоянии ожидания I/O операций, освобождая GIL для других потоков. Однако, по сравнению с `asyncio`, управление потоками и синхронный характер сетевых запросов и работы с БД все равно приводят к менее оптимальному использованию ресурсов.

## Общий вывод по лабораторной работе

Данная лабораторная работа наглядно продемонстрировала фундаментальные различия и оптимальные сценарии применения **`threading`**, **`multiprocessing`** и **`asyncio`** в Python.

* Для **CPU-bound задач**, где требуются интенсивные вычисления и обработка данных (например, подсчет большой суммы чисел), **`multiprocessing` является явным лидером**. Он позволяет обойти Global Interpreter Lock, создавая отдельные процессы, которые могут эффективно использовать несколько ядер процессора для истинного параллелизма. `threading` и `asyncio` в таких сценариях показывают схожую производительность с однопоточной моделью из-за ограничений GIL или отсутствия истинного параллелизма.

* Для **I/O-bound задач**, где основное время тратится на ожидание внешних операций (например, сетевые запросы, работа с файлами, базами данных), **`asyncio` демонстрирует наилучшую производительность**. Его событийная модель позволяет эффективно управлять тысячами одновременных операций ввода-вывода в одном потоке, минимизируя накладные расходы на переключение контекста. `threading` также показывает хорошие результаты в таких задачах, поскольку потоки могут освобождать GIL во время ожидания I/O. `multiprocessing` хоть и обеспечивает параллелизм, но его накладные расходы на создание и управление процессами могут быть избыточными для задач, которые в основном ждут.

**Ключевой вывод:** Выбор между `threading`, `multiprocessing` и `asyncio` должен основываться на природе решаемой задачи:

* Используйте **`multiprocessing`** для **CPU-bound** задач, требующих максимальной вычислительной мощности.
* Используйте **`asyncio`** для **I/O-bound** задач, где важна высокая конкурентность и эффективное управление ожиданием.
* Используйте **`threading`** для простых **I/O-bound** задач, когда не требуется максимальная производительность или когда асинхронный подход слишком сложен для реализации.

Правильный выбор подхода к параллельным вычислениям является критически важным для достижения оптимальной производительности и эффективности использования ресурсов в Python-приложениях.