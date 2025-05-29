# Лабораторная работа 2. Потоки. Процессы. Асинхронность.
## Задача 1. Различия между threading, multiprocessing и async в Python

Реализованный async:  
```
import asyncio# Лабораторная работа 2. Потоки. Процессы. Асинхронность.

import time

async def calculate_partial_sum(start, end):
    return sum(range(start, end))

async def main():
    start_time = time.time()
    n_tasks = 4
    total = 1000000000
    chunk_size = total // n_tasks
    tasks = [calculate_partial_sum(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(n_tasks)]

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    print("Total sum:", total_sum)
    print("Time:", time.time() - start_time)
    # Time: 30.117953777313232

if __name__ == "__main__":
    asyncio.run(main())
```

В следующем фрагмента создаеются список асинхронных задач для параллельного вычисления частных сумм , и каждая задача получает определенный
диапазон для расчета.  
chunk_size как раз таки размер части работы для каждой задачи. То есть разбивеам на раные части относительно основного числа.  
```
    tasks = [calculate_partial_sum(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(n_tasks)]
```

Реализованный threading: 
```
import threading
import time

def calculate_partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def main():
    start_time = time.time()
    n_threads = 4
    total = 1000000000
    chunk_size = total // n_threads
    threads = []
    results = [0] * n_threads

    for i in range(n_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        t = threading.Thread(target=calculate_partial_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_sum = sum(results)
    print("Total sum:", total_sum)
    print("Time:", time.time() - start_time)
    # Time: 31.38943386077881

if __name__ == "__main__":
    main()
```

```
t = threading.Thread(target=calculate_partial_sum, args=(start, end, results, i))
threads.append(t)
t.start()
```
В этой части создаются потоки и рассчитанный диапазон чисел для каждого потока.  

Реализованный multiprocessing: 
```
import multiprocessing
import time

def calculate_partial_sum(start, end):
    return sum(range(start, end))

def main():
    start_time = time.time()
    n_processes = 4
    total = 1000000000
    chunk_size = total // n_processes
    pool = multiprocessing.Pool(processes=n_processes)
    tasks = [(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(n_processes)]

    results = pool.starmap(calculate_partial_sum, tasks)
    pool.close()
    pool.join()

    total_sum = sum(results)
    print("Total sum:", total_sum)
    print("Time:", time.time() - start_time)
    # Time: 21.549757957458496

if __name__ == "__main__":
    main()
```
Здесь создается пул из 4  процессов. Эти процессы будут существовать до закрытия пула. Здесь через кортежи генерируется список
и затем каждый кортеж получает свою часть вычислений.  

Время вычисления:  
asyncio   # Time: 30.117953777313232  
threading  # Time: 31.38943386077881  
multiprocessing  # Time: 21.549757957458496  
Для вычислительных задач наиболее эффективен multiprocessing  

## Задача 2. Параллельный парсинг веб-страниц с сохранением в базу данных

Для извлечения информации о турах я написала parser.py  
```
from bs4 import BeautifulSoup


URLS = [
    "https://www.tourradar.com/srp/d-bulgaria",
    "https://www.tourradar.com/srp/d-benin",
    "https://www.tourradar.com/srp/d-kenya",
    "https://www.tourradar.com/srp/d-andorra",
    "https://www.tourradar.com/srp/d-japan",
    "https://www.tourradar.com/srp/d-greenland"
]

def extract_tours_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    tour_cards = soup.find_all("div", class_="js-ao-serp-tour-card")
    results = []

    for card in tour_cards:
        try:
            title_tag = card.find("h3", class_="ao-serp-tour-card__title")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            destination_tag = card.find("dt", string="Destinations")
            destination = destination_tag.find_next("dd").get_text(strip=True).split(",")[0] if destination_tag else "N/A"

            age_tag = card.find("dt", string="Age Range")
            age_range = age_tag.find_next("dd").get_text(strip=True) if age_tag else "N/A"

            duration_block = card.find("dl", class_="ao-serp-tour-card__detail-item--duration")
            duration_days = duration_block.find("dd").get_text(strip=True) if duration_block else "N/A"
            results.append({
                "title": title,
                "destination": destination,
                "age": age_range,
                "duration": duration_days
            })
        except Exception as inner_e:
            print(f"Ошибка при парсинге: {inner_e}")
    return results
```
Подключение к БД и модель данных для хранения информации:  
```
from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/trip_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TripRealParser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    destination: str
    age: str
    duration: str

SQLModel.metadata.create_all(engine)
```
Далее основные функции:

asyncio:  

```
async_engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/trip_db")
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def parse_tour_page_async(url):
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                html = await response.text()
                return extract_tours_from_html(html)
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return []

async def parse_and_save_async(url):
    tours = await parse_tour_page_async(url)
    async with AsyncSessionLocal() as session:
        for data in tours:
            trip = TripRealParser(**data)
            session.add(trip)
        await session.commit()
        print(f"Сохранено: {len(tours)} туров с {url}")

async def main():
    tasks = [parse_and_save_async(url) for url in URLS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(main())
    print(f"Время выполнения Async: {time.time() - start:.7f} сек")
```
Создаётся асинхронное подключение к PostgreSQL. Фабрика сессий AsyncSessionLocal создает асинхронные сессии для работы с БД.  
Здесь создаются и параллельно выполняются задачи парсинга для всех URL из списка.
```
async def main():
    tasks = [parse_and_save_async(url) for url in URLS]
    await asyncio.gather(*tasks)
```
![img_1.png](img_1.png)  

threading  
```
import time
import requests
import threading
from db import TripRealParser, SessionLocal
from parser import extract_tours_from_html, URLS

def parse_tour_page(url):
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        return extract_tours_from_html(html)
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return []

def parse_and_save_threading(url):
    tours = parse_tour_page(url)
    if tours:
        with SessionLocal() as session:
            for data in tours:
                trip = TripRealParser(**data)
                session.add(trip)
            session.commit()
            print(f"Сохранено: {len(tours)} туров с {url}")

def main():
    start = time.time()

    threads = []

    for url in URLS:
        thread = threading.Thread(target=parse_and_save_threading, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Время выполнения Threading: {time.time() - start:.7f} сек")

if __name__ == "__main__":
    main()
```
В основной функции создается и запускается поток для каждого URL где она и обрабатывается,
каждый поток парсит данные и сохраняет в бд. Основной поток ожидает завершения всех дочерних потоков.  
![img_2.png](img_2.png)  

multiprocessing
```
import time
import requests
import multiprocessing
from db import TripRealParser, SessionLocal
from parser import extract_tours_from_html, URLS

def parse_tour_page(url):
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        return extract_tours_from_html(html)
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return []

def parse_and_save(url):
    tours = parse_tour_page(url)
    with SessionLocal() as session:
        for data in tours:
            trip = TripRealParser(**data)
            session.add(trip)
        session.commit()
        print(f"Сохранено: {len(tours)} туров с {url}")

def main():
    start = time.time()

    processes = []

    for url in URLS:
        process = multiprocessing.Process(target=parse_and_save, args=(url,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print(f"Время выполнения Multiprocessing: {time.time() - start:.7f} сек")

if __name__ == "__main__":
    main()
```
Создается отдельный процесс для каждого URL.  
![img_3.png](img_3.png)  

![img.png](img.png)
![img_4.png](img_4.png)
