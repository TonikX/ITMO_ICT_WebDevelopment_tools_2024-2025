# Лабораторная работа 2: Потоки, процессы, асинхронность

## Задача 1: Сравнение threading, multiprocessing и async в Python

### Цель:
Исследовать различия между тремя подходами параллельных вычислений в Python — потоками, процессами и асинхронностью — на примере задачи суммирования чисел от 1 до 10 триллионов.


### Условие:
Каждая программа должна вычислять сумму чисел от 1 до 10_000_000_000, делая это параллельно с использованием:

- `threading`

- `multiprocessing`

- `asyncio`


### Реализация:

#### Файл: `threading_sum.py`
Используется модуль `threading`, создаются 4 потока, каждый считает свою часть суммы и записывает результат в общий список.

```python
import threading
import time

def calculate_sum(start, end, results, index):
    results[index] = sum(range(start, end + 1))

def main():
    N = 10_000_000_000  
    NUM_THREADS = 4
    step = N // NUM_THREADS
    results = [0] * NUM_THREADS
    threads = []

    t0 = time.time()
    for i in range(NUM_THREADS):
        start_range = i * step + 1
        end_range = (i + 1) * step if i < NUM_THREADS - 1 else N
        t = threading.Thread(target=calculate_sum, args=(start_range, end_range, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    print("Threading result:", total)
    print("Time:", time.time() - t0, "seconds")

if __name__ == "__main__":
    main()
```

#### Файл: `multiprocessing_sum.py`

Используется модуль multiprocessing. Каждый процесс отправляет свой результат в очередь multiprocessing.Queue, откуда они собираются в основном процессе.

```python
import multiprocessing
import time

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end + 1)))

def main():
    N = 10_000_000_000
    NUM_PROCESSES = 4
    step = N // NUM_PROCESSES
    queue = multiprocessing.Queue()
    processes = []

    t0 = time.time()
    for i in range(NUM_PROCESSES):
        start_range = i * step + 1
        end_range = (i + 1) * step if i < NUM_PROCESSES - 1 else N
        p = multiprocessing.Process(target=calculate_sum, args=(start_range, end_range, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(queue.get() for _ in range(NUM_PROCESSES))
    print("Multiprocessing result:", total)
    print("Time:", time.time() - t0, "seconds")

if __name__ == "__main__":
    main()
```

#### Файл: asyncio_sum.py

Асинхронная реализация. Используется asyncio.create_task() и await asyncio.gather(...) для параллельного запуска корутин, каждая из которых считает сумму своего диапазона.

```python
import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    N = 10_000_000_000
    NUM_TASKS = 4
    step = N // NUM_TASKS

    tasks = []
    for i in range(NUM_TASKS):
        start_range = i * step + 1
        end_range = (i + 1) * step if i < NUM_TASKS - 1 else N
        tasks.append(asyncio.create_task(calculate_sum(start_range, end_range)))

    t0 = time.time()
    results = await asyncio.gather(*tasks)
    total = sum(results)
    print("Asyncio result:", total)
    print("Time:", time.time() - t0, "seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

## Результаты измерений:

### asyncio_sum.py 
Asyncio result: 50000000005000000000

Time: 130.47408509254456 seconds

### threading_sum.py 
Threading result: 50000000005000000000

Time: 132.37248992919922 seconds

### multiprocessing_sum.py 
Multiprocessing result: 50000000005000000000

Time: 43.91871190071106 seconds
