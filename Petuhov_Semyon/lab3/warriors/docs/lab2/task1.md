# Offer
Задача 1. Различия между threading, multiprocessing и async в Python
Задача: Напишите три различных программы на Python, 
использующие каждый из подходов: threading, multiprocessing и async. 
Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. 
Разделите вычисления на несколько параллельных задач для ускорения выполнения.

Были написаны 3 различные реализации 

threading
```python
# threading_sum.py
import threading
import time

TOTAL = 10_000_000_000
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
Результат:
Threading total sum: 50000000005000000000
Threading duration: 403.50 seconds

async
```python
# async_sum.py
import asyncio
import time

TOTAL = 10_000_000_000
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

Результат:
Async total sum: 50000000005000000000
Async duration: 405.61 seconds

multiprocessing
```python
# multiprocessing_sum.py
from multiprocessing import Process, Array
import time
import os

TOTAL = 10_000_000_000
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

Результаты:
Multiprocessing total sum: 50000000005000000000
Multiprocessing duration: 68.15 seconds

Общие результаты:
Threading - 403.50 секунд

Async - 405.61 секунд

Multiprocessing - 68.15 секунд

Как и ожидалось только Async дал реальную прибавку в производительности, т.к. он реализует настоящий параллелизм и соответсвенно более эффективно выполняет задачу
