# Лабораторная работа: Сравнение способов параллельного выполнения в Python

## Задание 1: Вычисление суммы чисел с использованием threading, multiprocessing и async

### Цель задания

Сравнить три подхода к параллельному выполнению задач в Python: threading, multiprocessing и async/await, путем
реализации вычисления суммы чисел от 1 до 10,000,000 (десяти миллионов) с разделением задачи на несколько параллельных
подзадач.

### Описание программ

#### 1. Threading подход (`sum_threading.py`)

**Принцип работы:**
Threading использует потоки операционной системы, которые разделяют общую память процесса. В Python из-за GIL (Global
Interpreter Lock) потоки не могут выполняться параллельно в CPU-bound задачах, но могут быть полезны для I/O-bound
задач.

```python
import threading
import time


def calculate_sum_part(start, end, result_dict, thread_id):
    """Вычисляет сумму чисел в заданном диапазоне"""
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result_dict[thread_id] = partial_sum
    print(f"Thread {thread_id}: от {start} до {end} = {partial_sum}")


def calculate_sum_threading(n, num_threads=4):
    """Вычисляет сумму чисел от 1 до n используя threading"""
    chunk_size = n // num_threads
    threads = []
    result_dict = {}

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        if i == num_threads - 1:
            end = n
        else:
            end = (i + 1) * chunk_size

        thread = threading.Thread(
            target=calculate_sum_part,
            args=(start, end, result_dict, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result_dict.values())
    end_time = time.time()

    print(f"\nThreading общая сумма: {total_sum}")
    print(f"время затрачено: {end_time - start_time:.2f} seconds")
    return total_sum


if __name__ == "__main__":
    n = 10_000_000  # 10 миллионов
    calculate_sum_threading(n)
    # Время выполнения: ~0.29 секунд
```

#### 2. Multiprocessing подход (`sum_multiprocessing.py`)

**Принцип работы:**
Multiprocessing использует отдельные процессы операционной системы, каждый со своей памятью и экземпляром интерпретатора
Python. Это обходит ограничение GIL и позволяет использовать все ядра CPU для параллельных вычислений.

```python
import multiprocessing
import time


def calculate_sum_part(start, end, result_queue, process_id):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result_queue.put((process_id, partial_sum))
    print(f"процесс {process_id}: вычислена сумма с {start} по {end} = {partial_sum}")


def calculate_sum_multiprocessing(n, num_processes=4):
    chunk_size = n // num_processes
    processes = []
    result_queue = multiprocessing.Queue()

    start_time = time.time()

    for i in range(num_processes):
        start = i * chunk_size + 1
        if i == num_processes - 1:
            end = n  # Последний процесс обрабатывает оставшиеся числа
        else:
            end = (i + 1) * chunk_size

        process = multiprocessing.Process(
            target=calculate_sum_part,
            args=(start, end, result_queue, i)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get()[1])

    total_sum = sum(results)
    end_time = time.time()

    print(f"\nMultiprocessing сумма: {total_sum}")
    print(f"время затрачено: {end_time - start_time:.2f} seconds")
    return total_sum


if __name__ == "__main__":
    n = 10_000_000  # 10 миллионов
    calculate_sum_multiprocessing(n)
    # Время выполнения: ~0.17 секунд
```

#### 3. Async подход (`sum_asyncio.py`)

**Принцип работы:**
Async/await использует кооперативную многозадачность внутри одного потока. Задачи самостоятельно уступают управление в
ожидаемых точках, что особенно эффективно для I/O-bound задач, но может быть полезно и для CPU-bound задач с
периодической передачей управления.

```python
import asyncio
import time


async def calculate_sum_part_async(start, end, task_id):
    """Асинхронно вычисляет сумму чисел в заданном диапазоне"""
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
        if i % 1_000_000 == 0:
            await asyncio.sleep(0.000001)
    print(f"таск {task_id}: вычислил с {start} по {end} = {partial_sum}")
    return partial_sum


async def calculate_sum_async(n, num_tasks=4):
    """Вычисляет сумму чисел от 1 до n используя async/await"""
    chunk_size = n // num_tasks

    start_time = time.time()

    # Создаем список задач
    tasks = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        if i == num_tasks - 1:
            end = n  # Последняя задача обрабатывает оставшиеся числа
        else:
            end = (i + 1) * chunk_size

        task = calculate_sum_part_async(start, end, i)
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"\nAsync сумма: {total_sum}")
    print(f"время затрачено: {end_time - start_time:.2f} seconds")
    return total_sum


if __name__ == "__main__":
    n = 10_000_000
    asyncio.run(calculate_sum_async(n))
    # Время выполнения: ~0.56 секунд
```

### Анализ результатов

#### Измерение времени выполнения:

| Подход          | Время выполнения (сек) |
|-----------------|------------------------|
| Threading       | 0.29                   |
| Multiprocessing | 0.17                   |
| Async           | 0.56                   |

#### Вывод:

1. **Multiprocessing** показал лучшие результаты (0.17 сек), что объясняется возможностью параллельного выполнения на
   разных ядрах CPU и отсутствием ограничений GIL для CPU-bound задач.

2. **Threading** показал средние результаты (0.29 сек), что объясняется ограничениями GIL в Python, не позволяющими
   параллельное выполнение потоков для CPU-bound задач. Однако, из-за более низких накладных расходов на создание
   потоков по сравнению с процессами, он все равно показывает приемлемую производительность.

3. **Async** показал самые низкие результаты (0.56 сек), что объясняется тем, что этот подход лучше подходит для
   I/O-bound задач, а не для CPU-bound операций. В данном случае, вызовы `await asyncio.sleep()` вносят дополнительные
   задержки.

