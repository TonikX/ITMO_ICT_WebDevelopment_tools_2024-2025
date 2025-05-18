# Лабораторная работа: Сравнение методов парсинга веб-страниц с использованием threading, multiprocessing и async

## Задание 2: Разработка парсера веб-страниц с использованием различных подходов параллельного выполнения

### Цель задания

Разработать три разных программы для парсинга веб-страниц, использующие threading, multiprocessing и async/await. Каждая
программа должна загружать HTML-страницу, парсить данные и сохранять их в базу данных. Сравнить производительность
каждого подхода и проанализировать их преимущества и недостатки.

### Описание программ

В данной работе рассматриваются три подхода к параллельному парсингу веб-страниц:

1. **Threading** - использование модуля `threading`
2. **Multiprocessing** - использование модуля `multiprocessing`
3. **Async** - использование async/await и модуля `aiohttp`

Все программы реализуют парсинг данных о хоккейных командах с различных спортивных сайтов и сохраняют информацию в базу
данных PostgreSQL.

#### Общие функциональные возможности программ:

- Парсинг информации о командах из нескольких источников
- Поддержка обхода SSL-сертификатов для проблемных сайтов
- Извлечение названий команд, городов, стран и другой информации
- Сохранение данных в существующую базу данных
- Измерение времени выполнения

### Структура программ

#### 1. Threading подход (`threading_parser_sports.py`)

**Принцип работы:**
Программа создает отдельные потоки для каждого URL, которые параллельно загружают страницы и парсят данные. Для
обеспечения потокобезопасности используется блокировка при работе с базой данных.

```python
import threading
import requests
from bs4 import BeautifulSoup
import psycopg2
import time

# ... дополнительные импорты

# Блокировка для потокобезопасной работы с БД
db_lock = threading.Lock()


def parse_and_save_threading(url_info, thread_id):
    """Парсинг страницы и сохранение в БД"""
    url = url_info['url']
    data_type = url_info['type']

    try:
        # Создаем сессию с SSL адаптером
        session = requests.Session()
        session.mount('https://', SSLAdapter())

        # Получаем страницу
        response = session.get(url, headers=headers, timeout=15, verify=False)

        # Парсим HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        if data_type == 'teams':
            teams = parse_team_info(soup, url)

            # Сохраняем в БД (потокобезопасно)
            with db_lock:
                conn = get_db_connection()
                # Код для сохранения в БД
                conn.close()

        return True
    except Exception as e:
        print(f"Thread {thread_id}: Error parsing {url}: {e}")
        return False


def threading_parser(url_list, num_threads=3):
    """Основная функция для threading подхода"""
    init_database()
    clear_database()
    start_time = time.time()

    # Разделяем URL между потоками
    threads = []

    for i in range(min(num_threads, len(url_list))):
        # Создаем потоки для обработки URL
        thread = threading.Thread(
            target=lambda urls, tid: [parse_and_save_threading(url, tid) for url in urls],
            args=(thread_urls, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"\nThreading completed in {end_time - start_time:.2f} seconds")
```

#### 2. Multiprocessing подход (`multiprocessing_parser_sports.py`)

**Принцип работы:**
Программа создает отдельные процессы для каждого URL, которые параллельно загружают страницы и парсят данные. Каждый
процесс имеет свою собственную память и подключение к базе данных.

```python
import multiprocessing
import requests
from bs4 import BeautifulSoup
import psycopg2
import time


# ... дополнительные импорты

def parse_and_save_process(url_info, process_id):
    """Функция для парсинга в отдельном процессе"""
    url = url_info['url']
    data_type = url_info['type']

    try:
        session = requests.Session()
        session.mount('https://', SSLAdapter())

        # Получаем страницу
        response = session.get(url, headers=headers, timeout=15, verify=False)

        soup = BeautifulSoup(response.content, 'html.parser')

        if data_type == 'teams':
            teams = parse_team_info(soup, url)

            # Сохраняем в БД
            conn = get_db_connection()
            # Код для сохранения в БД
            conn.close()

        return True
    except Exception as e:
        print(f"Process {process_id}: Error parsing {url}: {e}")
        return False


def multiprocessing_parser(url_list, num_processes=None):
    """Основная функция для multiprocessing подхода"""
    if num_processes is None:
        num_processes = min(multiprocessing.cpu_count(), len(url_list))

    init_database()
    clear_database()
    start_time = time.time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        args = [(url_info, i) for i, url_info in enumerate(url_list)]
        results = pool.starmap(parse_and_save_process, args)

    end_time = time.time()
    print(f"\nMultiprocessing completed in {end_time - start_time:.2f} seconds")
```

#### 3. Async подход (`async_parser_sports.py`)

**Принцип работы:**
Программа создает асинхронные задачи для каждого URL, которые конкурентно загружают страницы и парсят данные в рамках
одного процесса. Использует `aiohttp` для асинхронных HTTP-запросов и `asyncpg` для асинхронной работы с базой данных.

```python
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
import time


# ... дополнительные импорты

async def init_database():
    """Инициализация пула соединений с БД"""
    return await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=1,
        max_size=10
    )


async def parse_and_save_async(session, pool, url_info, task_id):
    url = url_info['url']
    data_type = url_info['type']

    try:
        # Создаем SSL контекст с сертификатами
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with session.get(url, headers=headers, ssl=ssl_context, timeout=15) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                if data_type == 'teams':
                    teams = parse_team_info(soup, url)

                    # Сохраняем в БД асинхронно
                    async with pool.acquire() as conn:
                        # Асинхронный код для сохранения в БД
                        pass

        return True
    except Exception as e:
        print(f"Task {task_id}: Error parsing {url}: {e}")
        return False


async def async_parser(url_list):
    start_time = time.time()

    pool = await init_database()

    try:
        await clear_database(pool)

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i, url_info in enumerate(url_list):
                task = parse_and_save_async(session, pool, url_info, i)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        end_time = time.time()
        print(f"\nAsync completed in {end_time - start_time:.2f} seconds")

    finally:
        await pool.close()
```

### Анализ результатов

#### Результаты сравнения времени выполнения:

| Подход          | Время выполнения (сек) | Команды | Школы | Турниры |
|-----------------|------------------------|---------|-------|---------|
| Threading       | 3.36                   | 69      | 69    | 2       |
| Multiprocessing | 1.14                   | 69      | 69    | 2       |
| Async           | 1.19                   | 69      | 69    | 2       |

**Выводы:**

- **Самый быстрый**: Multiprocessing (1.14 секунд)
- **Самый медленный**: Threading (3.36 секунд)
- **Разница**: 2.22 секунд (в 2.95 раза)

#### Сравнение подходов

1. **Threading**:
    - **Преимущества**:
        - Низкие накладные расходы на создание потоков
        - Общая память между потоками
        - Простота реализации
    - **Недостатки**:
        - Ограничение GIL (Global Interpreter Lock) в Python
        - Необходимость использования блокировок для безопасной работы с общими ресурсами
        - Худшая производительность для CPU-bound задач
    - **Результат парсинга**: Работает медленнее других подходов (3.36 секунд)

2. **Multiprocessing**:
    - **Преимущества**:
        - Обход ограничения GIL
        - Параллельное выполнение на разных ядрах CPU
        - Изоляция процессов друг от друга
    - **Недостатки**:
        - Высокие накладные расходы на создание процессов
        - Отсутствие общей памяти (необходимость сериализации данных)
        - Сложности с отладкой
    - **Результат парсинга**: Самый быстрый подход (1.14 секунд)

3. **Async**:
    - **Преимущества**:
        - Высокая масштабируемость для I/O-bound задач
        - Низкие накладные расходы (по сравнению с процессами)
        - Упрощенная синхронизация задач
    - **Недостатки**:
        - Сложность разработки и отладки
        - Требует специальных асинхронных библиотек
        - Не обходит ограничение GIL для CPU-bound задач
    - **Результат парсинга**: Близок к multiprocessing (1.19 секунд)

### Заключение

Для задачи парсинга веб-страниц и сохранения данных в базу данных наилучшие результаты продемонстрировал подход с
использованием **multiprocessing** (1.14 секунд), за которым следует **async** (1.19 секунд). **Threading** показал
значительно худший результат (3.36 секунд).

Такое распределение результатов объясняется тем, что парсинг веб-страниц является смешанной задачей, включающей как
I/O-операции (загрузка страниц), так и CPU-операции (обработка HTML). Multiprocessing эффективно распределяет нагрузку
между ядрами процессора, а async оптимизирует ожидание ответов от серверов, что делает эти два подхода более
эффективными для данного типа задач.

В зависимости от конкретных требований к проекту, можно выбирать между multiprocessing (для максимальной
производительности) и async (для лучшей масштабируемости с большим количеством URL).
