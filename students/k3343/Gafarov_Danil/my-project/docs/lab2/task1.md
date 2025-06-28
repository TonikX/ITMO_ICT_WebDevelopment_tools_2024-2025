# Лабораторная работа №2 - Потоки. Процессы. Асинхронность.

## Цель:
Понять отличия потоками и процессами и понять, что такое ассинхронность в Python.

Работа о потоках, процессах и асинхронности поможет студентам развить навыки создания эффективных и быстродействующих программ, что важно для работы с большими объемами данных и выполнения вычислений.

## Задача 1. Различия между threading, multiprocessing и async в Python
Задача: Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.

Threading — Потоки
1. Описание: Позволяет запускать несколько потоков (threads) в рамках одного процесса.
2. Подходит для: I/O-bound задач (ожидание сетевых запросов, чтение/запись файлов).
3. Ограничение: Глобальная блокировка интерпретатора (GIL) не позволяет выполнять Python-байткод параллельно в нескольких потоках на уровне CPU-bound задач.
4. Память: Потоки разделяют память, проще синхронизация.
5. Библиотека: threading
**threading_sum**

```
import threading
import time

TOTAL = 1_000_000_000
THREADS = 4

def calculate_sum(start, end, result, index):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result[index] = partial_sum

def main():
    step = TOTAL // THREADS
    threads = []
    result = [0] * THREADS

    start_time = time.time()

    for i in range(THREADS):
        start = i * step + 1
        end = (i + 1) * step if i != THREADS - 1 else TOTAL
        thread = threading.Thread(target=calculate_sum, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result)
    end_time = time.time()

    print(f"Threading: Сумма = {total_sum}, время = {end_time - start_time:.4f} сек")
```
**Результат выполнения**
Threading: Сумма = 500000000500000000, время = 48.5987 сек

**Multiprocessing — Процессы**
1. Описание: Создаёт отдельные процессы, каждый со своим интерпретатором Python и памятью.
2. Подходит для: CPU-bound задач (массивные вычисления, сложные алгоритмы).
3. Преимущество: Обходит GIL, процессы работают параллельно на разных ядрах CPU.
4. Память: Процессы не разделяют память (используются очереди, пайпы и т.п. для обмена данными).
5. Библиотека: multiprocessing

**multiprocessing_sum.py**
```
import multiprocessing
import time

TOTAL = 1_000_000_000
PROCESSES = 4

def calculate_sum(args):
    start, end = args
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    return partial_sum

def main():
    step = TOTAL // PROCESSES
    pool_args = []

    start_time = time.time()

    for i in range(PROCESSES):
        start = i * step + 1
        end = (i + 1) * step if i != PROCESSES - 1 else TOTAL
        pool_args.append((start, end))

    with multiprocessing.Pool(PROCESSES) as pool:
        results = pool.map(calculate_sum, pool_args)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Multiprocessing: Сумма = {total_sum}, время = {end_time - start_time:.4f} сек")
```
**Результат выполнения**
Multiprocessing: Сумма = 500000000500000000, время = 18.2911 сек

Async - Асинхронность
1. Описание: Использует событийный цикл (event loop) для асинхронного выполнения задач без блокировки.
2. Подходит для: I/O-bound задач, высокой производительности в большом числе соединений (например, сетевые сервера).
3. Параллелизм: Не настоящий параллелизм, а кооперативная многозадачность — задачи уступают управление вручную.
4. Память: Всё происходит в одном потоке, одной памяти.
5. Библиотека: asyncio

**async_sum.py**
```
import asyncio
import time

TOTAL = 1_000_000_000
TASKS = 4

async def calculate_sum(start, end):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    return partial_sum

async def main():
    step = TOTAL // TASKS
    tasks = []

    start_time = time.time()

    for i in range(TASKS):
        start = i * step + 1
        end = (i + 1) * step if i != TASKS - 1 else TOTAL
        task = asyncio.create_task(calculate_sum(start, end))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    end_time = time.time()

    print(f"Asyncio: Сумма = {total_sum}, время = {end_time - start_time:.4f} сек")
```

**Результат выполнения**
Asyncio: Сумма = 500000000500000000, время = 56.0137 сек


Multiprocessing — Лучшая производительность для CPU-bound задач

Каждый процесс запускается независимо и получает своё собственное ядро (если доступно), что позволяет выполнять настоящий параллелизм.
Python-интерпретатор (CPython) использует GIL (Global Interpreter Lock), который ограничивает параллельное выполнение Python-байткода. multiprocessing обходит это, поскольку процессы не делят GIL.