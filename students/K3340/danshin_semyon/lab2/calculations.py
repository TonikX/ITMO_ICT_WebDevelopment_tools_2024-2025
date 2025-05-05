import threading
import multiprocessing
import asyncio
import time


def calculate_sum_threading(start, end, result, index):
    total = sum(range(start, end + 1))
    result[index] = total

def run_threading():
    start_time = time.time()
    n = 10_000_000_000
    num_threads = 4
    chunk_size = n // num_threads
    threads = []
    result = [0] * num_threads

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = start + chunk_size - 1 if i < num_threads - 1 else n
        thread = threading.Thread(target=calculate_sum_threading, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result)
    elapsed_time = time.time() - start_time
    return total_sum, elapsed_time

def calculate_sum_multiprocessing(start, end):
    return sum(range(start, end + 1))

def run_multiprocessing():
    start_time = time.time()
    n = 10_000_000_000
    num_processes = 4
    chunk_size = n // num_processes
    pool = multiprocessing.Pool(processes=num_processes)
    ranges = [(i * chunk_size + 1, i * chunk_size + chunk_size) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], n)

    results = pool.starmap(calculate_sum_multiprocessing, ranges)
    pool.close()
    pool.join()

    total_sum = sum(results)
    elapsed_time = time.time() - start_time
    return total_sum, elapsed_time

async def calculate_sum_async(start, end):
    return sum(range(start, end + 1))

async def run_async():
    start_time = time.time()
    n = 10_000_000_000
    num_tasks = 4
    chunk_size = n // num_tasks
    tasks = []

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = start + chunk_size - 1 if i < num_tasks - 1 else n
        tasks.append(calculate_sum_async(start, end))

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    elapsed_time = time.time() - start_time
    return total_sum, elapsed_time


def generate_documentation(threading_time1, multiprocessing_time1, async_time1):
    doc = f"""
# Лабораторная работа 2: Потоки, процессы и асинхронность

## Обзор
В этой лабораторной работе демонстрируется использование потоков, многопроцессности и асинхронного подхода в Python для решения двух задач:
1. Вычисление суммы чисел от 1 до 10 000 000.
2. Параллельный парсинг веб-страниц и сохранение заголовков в базу данных SQLite.

## Задача 1: Вычисление суммы

### Подход с потоками (Threading)
- **Описание**: Использует модуль `threading` для создания нескольких потоков, каждый из которых вычисляет сумму части диапазона.
- **Реализация**: Делит диапазон на 4 части, каждой назначает поток и агрегирует результаты.
- **Особенности**:
  - Ограничен GIL Python, поэтому не обеспечивает настоящий параллелизм для задач, нагружающих CPU.
  - Создание потоков легче по ресурсам по сравнению с процессами.
- **Время выполнения**: {threading_time1:.2f} секунд

### Подход с многопроцессностью (Multiprocessing)
- **Описание**: Использует модуль `multiprocessing` для создания отдельных процессов для параллельного вычисления суммы.
- **Реализация**: Делит диапазон на 4 части, распределяет их между процессами с использованием пула процессов.
- **Особенности**:
  - Обеспечивает настоящий параллелизм, обходя GIL, идеально подходит для задач с высокой нагрузкой на CPU.
  - Более высокие накладные расходы из-за создания процессов и межпроцессного взаимодействия.
- **Время выполнения**: {multiprocessing_time1:.2f} секунд

### Асинхронный подход (Async)
- **Описание**: Использует `asyncio` для асинхронного вычисления суммы.
- **Реализация**: Делит диапазон на 4 задачи и выполняет их параллельно с помощью `asyncio.gather`.
- **Особенности**:
  - Лучше всего подходит для задач, зависящих от ввода-вывода, неэффективен для задач, нагружающих CPU, таких как вычисление суммы.
  - Однопоточная конкурентность с использованием event loop.
- **Время выполнения**: {async_time1:.2f} секунд

## Сравнение производительности

| Подход          | Время выполнения (секунды) |
|------------------|----------------------------|
| Threading        | {threading_time1:.2f}                  |
| Multiprocessing  | {multiprocessing_time1:.2f}                |
| Async            | {async_time1:.2f}                    |

**Анализ**:
- **Multiprocessing** работает быстрее всего для этой CPU-нагруженной задачи, так как обходит GIL и использует несколько ядер процессора.
- **Threading** медленнее из-за ограничений GIL, препятствующих реальному параллелизму при вычислениях.
- **Async** самый медленный в данном случае, так как `asyncio` предназначен для задач с вводом-выводом, а суммирование — чисто вычислительная операция.
"""
    return doc

if __name__ == "__main__":
    print("Task 1: Sum Calculation")
    threading_sum, threading_time1 = run_threading()
    print(f"Threading: Sum = {threading_sum}, Time = {threading_time1:.2f} seconds")

    multiprocessing_sum, multiprocessing_time1 = run_multiprocessing()
    print(f"Multiprocessing: Sum = {multiprocessing_sum}, Time = {multiprocessing_time1:.2f} seconds")

    async_sum, async_time1 = asyncio.run(run_async())
    print(f"Async: Sum = {async_sum}, Time = {async_time1:.2f} seconds")

    doc = generate_documentation(threading_time1, multiprocessing_time1, async_time1)
    with open("lab2_report.md", "w") as f:
        f.write(doc)
    print("Documentation generated: lab2_report.md")
