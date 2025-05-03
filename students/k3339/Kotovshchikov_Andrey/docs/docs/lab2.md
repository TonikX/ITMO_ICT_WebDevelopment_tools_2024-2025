# Лабораторная работа 2. Потоки. Процессы. Асинхронность

#### [Ссылка](https://github.com/KotovshchikovAndrey/ITMO_ICT_WebDevelopment_tools_2024-2025/tree/lab2/students/k3339/Kotovshchikov_Andrey/Lab2)

## Задача 1. Различия между threading, multiprocessing и async в Python

Для выявления особенностей и различий между тремя подходами параллелизма была написана
небольшая программа, которая считает сумму чисел от **0 до 100_000_000**. Чтобы распараллелить вычисления
мы разбиваем сумму на подсуммы (количество подсумм равно количеству ядер процессора), а затем агрегируем результат.
Далее эта логика будет реализована при помощи **asyncio**, **threading** и **multiprocessing**.

### Asyncio

```python
import asyncio
import multiprocessing
import time


async def calculate_sum(start: int, end: int) -> int:
    return sum(num for num in range(start + 1, end + 1))


N = 100_000_000
MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
N_per_process = N // MAX_CONCURENCY


async def main() -> None:
    start_time = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tasks: list[asyncio.Task[int]] = []
        for offset in range(MAX_CONCURENCY):
            task = tg.create_task(
                calculate_sum(
                    start=offset * N_per_process,
                    end=offset * N_per_process + N_per_process,
                ),
            )

            tasks.append(task)

    print(f"Результат: {sum([task.result() for task in tasks])}")
    print(f"Время: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Результат:

```bash
python async.py
Результат: 5000000050000000
Время: 3.640345600026194
```

### Threading

```python
import multiprocessing
import time
from concurrent.futures import Future, ThreadPoolExecutor


def calculate_sum(start: int, end: int) -> int:
    return sum(num for num in range(start + 1, end + 1))


N = 100_000_000
MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
N_per_process = N // MAX_CONCURENCY


def main() -> None:
    start_time = time.perf_counter()
    with ThreadPoolExecutor(max_workers=MAX_CONCURENCY) as executor:
        futures: list[Future[int]] = []
        for offset in range(MAX_CONCURENCY):
            future = executor.submit(
                calculate_sum,
                start=offset * N_per_process,
                end=offset * N_per_process + N_per_process,
            )

            futures.append(future)

    print(f"Результат: {sum([future.result() for future in futures])}")
    print(f"Время: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    main()
```

### Результат:

```bash
python threads.py
Результат: 5000000050000000
Время: 3.6831088999751955
```

### Multiprocessing

```python
import multiprocessing
import time
from concurrent.futures import Future, ProcessPoolExecutor


def calculate_sum(start: int, end: int) -> int:
    return sum(num for num in range(start + 1, end + 1))


N = 100_000_000
MAX_CONCURENCY = multiprocessing.cpu_count()  # 8 cores
N_per_process = N // MAX_CONCURENCY


def main() -> None:
    start_time = time.perf_counter()
    with ProcessPoolExecutor(max_workers=MAX_CONCURENCY) as executor:
        futures: list[Future[int]] = []
        for offset in range(MAX_CONCURENCY):
            future = executor.submit(
                calculate_sum,
                start=offset * N_per_process,
                end=offset * N_per_process + N_per_process,
            )

            futures.append(future)

    print(f"Результат: {sum([future.result() for future in futures])}")
    print(f"Время: {time.perf_counter() - start_time}")


if __name__ == "__main__":
    main()
```

### Результат:

```bash
python processes.py
Результат: 5000000050000000
Время: 1.3969435000326484
```

### Итог

Результаты получились весьма предсказуемыми. Из-за особенностей реализации многопоточности в Python, а точнее такого миханизма как GIL, в каждый момент времени лишь один поток занимается вычислениями, в то время как остальные "спят", ожидая освобождения глобальной блокировки интерпритатора. В результате никакой "парралельности" мы не получаем, и время, потраченное на подсчет сумма ровно такое же, как у однопоточной программы на asyncio.

Самым быстрым оказался multiprocessing, так как на каждый процесс запускается свой интерпритатор
Python, у каждого из которых свой GIL. Благодаря этому мы получаем настоящую параллельность. Однако программа при таком подходе работает не в 8 раз быстрее (в моем примере было создано 8 процессов), а лишь в 2. Это связано с тем, что на компютере, на котором проводились замеры, запущено довольно много фоновых процессов, которые также требуют процессорного времени и не дают использовать все 8 доступных ядер процессора для получения восьмикратного выигрыша. Также не стоит забывать про время, затраченное на IPC (межпроцессное взаимодействие), и что само по себе создание процесса на уровни OC являтся довольно ресурснозатратным. Все это повлияло на итоговый результат.

## Задача 2. Параллельный парсинг веб-страниц с сохранением в базу данных

Далее по заданию необходимо было написать парсер с использованием трех подходов, рассмотренных выше.

### Asyncio

```python
import asyncio
import logging
import os

import aiohttp
import asyncpg
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def parse_and_save(url: str) -> None:
    logger.info("Start async parse: %s", url)
    connection: asyncpg.Connection = await asyncpg.connect(os.getenv("POSTGRES_URL"))
    logger.info("Connected to database")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                logger.error("Parse failed: %s", url)
                return

            soup = BeautifulSoup(await response.text(), features="html.parser")
            title = soup.find("title").text
            logger.info("Page title: %s", title)

            skills: set[str] = set()
            for row in soup.find("table").find("tbody").find_all("tr"):
                skill = row.get_text().split()[1]
                skills.add(skill)

            query = """INSERT INTO skill VALUES (DEFAULT, $1)
                ON CONFLICT (name) DO NOTHING;"""

            await connection.executemany(query, map(lambda skill: (skill,), skills))
            logger.info("Skills saved")

    await connection.close()
    logger.info("End async parse: %s", url)


async def main(urls: list[str]) -> None:
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(parse_and_save(url))
```

### Threading

```python
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import psycopg2
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_and_save(url: str) -> None:
    connection = psycopg2.connect(os.getenv("POSTGRES_URL"))
    cursor = connection.cursor()
    logger.info("Connected to database")

    skills: set[str] = set()
    logger.info("Start parse: %s", url)
    response = requests.get(url)
    if response.status_code != 200:
        logger.error("Parse failed: %s", url)
        return

    soup = BeautifulSoup(response.text, features="html.parser")
    title = soup.find("title").text
    logger.info("Page title: %s", title)

    for row in soup.find("table").find("tbody").find_all("tr"):
        skill = row.get_text().split()[1]
        skills.add(skill)

    query = """INSERT INTO skill VALUES (DEFAULT, %s)
        ON CONFLICT (name) DO NOTHING;"""

    cursor.executemany(query, map(lambda skill: (skill,), skills))
    connection.commit()
    logger.info("Skills saved")

    connection.close()
    logger.info("End parse: %s", url)


def main(urls: list[str]) -> None:
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(parse_and_save, urls)
```

### Multiprocessing

```python
import logging
import os
from concurrent.futures import ProcessPoolExecutor

import psycopg2
import requests
from bs4 import BeautifulSoup

from parsers.logger import setup_logger

logger = logging.getLogger(__name__)


def parse_and_save(url: str) -> None:
    # because another process
    setup_logger()

    connection = psycopg2.connect(os.getenv("POSTGRES_URL"))
    cursor = connection.cursor()
    logger.info("Connected to database")

    skills: set[str] = set()
    logger.info("Start parse: %s", url)
    response = requests.get(url)
    if response.status_code != 200:
        logger.error("Parse failed: %s", url)
        return

    soup = BeautifulSoup(response.text, features="html.parser")
    title = soup.find("title").text
    logger.info("Page title: %s", title)

    for row in soup.find("table").find("tbody").find_all("tr"):
        skill = row.get_text().split()[1]
        skills.add(skill)

    query = """INSERT INTO skill VALUES (DEFAULT, %s)
        ON CONFLICT (name) DO NOTHING;"""

    cursor.executemany(query, map(lambda skill: (skill,), skills))
    connection.commit()
    logger.info("Skills saved")

    connection.close()
    logger.info("End parse: %s", url)


def main(urls: list[str]) -> None:
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(parse_and_save, urls)
```

Результаты получились следующими:

```bash
python -m parsers --urls_path=urls.example --concurency=asyncio
[INFO] [2025-05-03 05:04:46] Start asyncio parser
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/1c_developer
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/c_sharp_developer
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/data_engineer
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/bi_analyst
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/devops
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/scala_developer
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/product_analyst
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/system_analyst
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/python_developer
[INFO] [2025-05-03 05:04:46] Start async parse: https://easyoffer.ru/analytic/pentester
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:46] Connected to database
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность C# Developer

[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность Product Analyst

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/c_sharp_developer
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/product_analyst
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность Scala Developer

[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность System Analyst

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/scala_developer
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/system_analyst
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность Data Engineer

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/data_engineer
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность BI Analyst

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/bi_analyst
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность Pentester

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/pentester
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность DevOps

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/devops
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность 1C Developer

[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] Page title:
Требования на должность Python Developer

[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/1c_developer
[INFO] [2025-05-03 05:04:47] Skills saved
[INFO] [2025-05-03 05:04:47] End async parse: https://easyoffer.ru/analytic/python_developer
[INFO] [2025-05-03 05:04:47] Stop asyncio parser | Time: 0.9342751000076532
```

```bash
python -m parsers --urls_path=urls.example --concurency=threads
[INFO] [2025-05-03 05:05:42] Start threads parser
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/system_analyst
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/devops
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/scala_developer
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/data_engineer
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/c_sharp_developer
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/pentester
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/bi_analyst
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/python_developer
[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность Scala Developer

[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/scala_developer
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/product_analyst
[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность C# Developer

[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность Python Developer

[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/c_sharp_developer
[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/python_developer
[INFO] [2025-05-03 05:05:42] Connected to database
[INFO] [2025-05-03 05:05:42] Start parse: https://easyoffer.ru/analytic/1c_developer
[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность DevOps

[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность System Analyst

[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/devops
[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/system_analyst
[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность BI Analyst

[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/bi_analyst
[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность Pentester

[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/pentester
[INFO] [2025-05-03 05:05:42] Page title:
Требования на должность Data Engineer

[INFO] [2025-05-03 05:05:42] Skills saved
[INFO] [2025-05-03 05:05:42] End parse: https://easyoffer.ru/analytic/data_engineer
[INFO] [2025-05-03 05:05:43] Page title:
Требования на должность Product Analyst

[INFO] [2025-05-03 05:05:43] Skills saved
[INFO] [2025-05-03 05:05:43] End parse: https://easyoffer.ru/analytic/product_analyst
[INFO] [2025-05-03 05:05:43] Page title:
Требования на должность 1C Developer

[INFO] [2025-05-03 05:05:43] Skills saved
[INFO] [2025-05-03 05:05:43] End parse: https://easyoffer.ru/analytic/1c_developer
[INFO] [2025-05-03 05:05:43] Stop threads parser | Time: 1.0321793000330217
```

```bash
python -m parsers --urls_path=urls.example --concurency=processes
[INFO] [2025-05-03 04:15:35] Start processes parser
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/system_analyst
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/scala_developer
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/product_analyst
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/bi_analyst
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/python_developer
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/devops
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/pentester
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/1c_developer
[INFO] [2025-05-03 04:15:36] Page title:
Требования на должность System Analyst

[INFO] [2025-05-03 04:15:36] Skills saved
[INFO] [2025-05-03 04:15:36] End parse: https://easyoffer.ru/analytic/system_analyst
[INFO] [2025-05-03 04:15:36] Connected to database
[INFO] [2025-05-03 04:15:36] Start parse: https://easyoffer.ru/analytic/data_engineer
[INFO] [2025-05-03 04:15:36] Page title:
Требования на должность BI Analyst

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/bi_analyst
[INFO] [2025-05-03 04:15:37] Connected to database
[INFO] [2025-05-03 04:15:37] Start parse: https://easyoffer.ru/analytic/c_sharp_developer
[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность DevOps

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/devops
[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность Python Developer

[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность Product Analyst

[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность Scala Developer

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/python_developer
[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/scala_developer
[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/product_analyst
[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность Pentester

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/pentester
[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность 1C Developer

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/1c_developer
[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность Data Engineer

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/data_engineer
[INFO] [2025-05-03 04:15:37] Page title:
Требования на должность C# Developer

[INFO] [2025-05-03 04:15:37] Skills saved
[INFO] [2025-05-03 04:15:37] End parse: https://easyoffer.ru/analytic/c_sharp_developer
[INFO] [2025-05-03 04:15:37] Stop processes parser | Time: 2.1589177999994718
```

Асинхронный подход оказался самым быстрым. Это связано с тем, что на этот раз в нашей программе преобладает IO-bound нагрузка (работа с сетью / сокетами), и лишь небольшая ее часть является CPU-bound (часть кода, где мы при помощи BeautifulSoup ищем нужную информацию внутри html страницы).
