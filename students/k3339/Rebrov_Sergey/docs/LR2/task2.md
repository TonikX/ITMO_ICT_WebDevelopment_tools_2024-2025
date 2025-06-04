## **Задание**

Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных. 
## **Таблица**

| Метод              | Время     | Комментарий                                                                      |
|--------------------|-----------|----------------------------------------------------------------------------------|
| `threading`        | 4.78 сек  | Потоки эффективно перекрывают I/O-операции                                       |
| `multiprocessing`  | 5.57 сек  | Неэффективен из-за накладных расходов на создание процессов                      |
| `asyncio`          | 4.21 сек  | Асинхронность позволяет не блокировать выполнение при ожидании ответа от сервера |


## **Файлы**

`threading_pr.py`
```python
def main():
    init_db()

    start = time.time()

    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"Время: {time.time() - start:.2f} сек")
```

`multiprocessing_pr.py`
```python
def main():
    init_db()

    start = time.time()

    processes = []
    for url in URLS:
        p = Process(target=parse_and_save, args=(url,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print(f"Время: {time.time() - start:.2f} сек")
```

`async_pr.py`
```python
async def main():
    init_db()

    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in URLS]
        await asyncio.gather(*tasks)

    print(f"Время: {time.time() - start:.2f} сек")
```