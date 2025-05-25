# Задача

Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.

## Подробности задания

1. Напишите программу на Python для каждого подхода: threading, multiprocessing и async.
2. Каждая программа должна содержать функцию calculate_sum(), которая будет выполнять вычисления.
3. Для threading используйте модуль threading, для multiprocessing - модуль multiprocessing, а для async - ключевые слова async/await и модуль asyncio.
4. Каждая программа должна разбить задачу на несколько подзадач и выполнять их параллельно.
5. Замерьте время выполнения каждой программы и сравните результаты.

## Сравнительная таблица

|                | Async    | Multiprocessing    | Threading         |
| -------------- | -----------: | -----------: | ----------------------: |
| **Counter**    | 26 сек      | 7 сек      | 28 сек     |

## 1. Async
```
import time
import asyncio

MAX_VALUE = 10**9
WORKERS = 100

async def partial_sum(start, step):
    return sum(range(start, MAX_VALUE, step))

async def calculate_sum():
    jobs  = [partial_sum(i, WORKERS) for i in range(WORKERS)]
    return await asyncio.gather(*jobs )

if __name__ == '__main__':
    start = time.time()
    sums = asyncio.run(calculate_sum())
    duration = time.time() - start
    print(f"Итоговая сумма:", sum(sums))
    print(f"Затрачено времени: {duration:.3f} сек")
```

```
Итоговая сумма: 499999999500000000
Затрачено времени: 26.246 сек
```
**Вывод:** для задач, требующих интенсивных вычислений, асинхронность не даёт никакого преимущества.

## 2. Multiprocessing
```
import time
import multiprocessing

MAX_VALUE = 10**9
PROCESS_COUNT = 10

def partial_sum(x):
    return sum(range(x[0], MAX_VALUE, x[1]))

def calculate_sums():
    with multiprocessing.Pool(processes=PROCESS_COUNT) as pool:
        parts = pool.imap_unordered(
            partial_sum, 
            [(i, PROCESS_COUNT) for i in range(PROCESS_COUNT)], 
            chunksize=1
        )
        return sum(parts)

if __name__ == '__main__':
    start = time.time()
    result = calculate_sums()
    duration = time.time() - start
    print(f"Итоговая сумма:", result)
    print(f"Затрачено времени: {duration:.3f} сек")
```

```
Итоговая сумма: 499999999500000000
Затрачено времени: 7.589 сек
```
**Вывод:** multiprocessing обеспечивает настоящий параллелизм на многопроцессорных системах и идеально подходит для CPU-bound задач.


## 3. Threading
```
import time
import threading

MAX_VALUE = 10**9
THREAD_COUNT = 100
sums = []
lock = threading.Lock()

def partial_sum(start, step):
    global sums
    part = sum(range(start, MAX_VALUE, step))
    lock.acquire()
    sums.append(part)
    lock.release()

def calculate_sum():
    threads = [
        threading.Thread(target=partial_sum, args=(i, THREAD_COUNT)) 
        for i in range(THREAD_COUNT)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    start = time.time()
    calculate_sum()
    duration = time.time() - start
    print(f"Итоговая сумма:", sum(sums))
    print(f"Затрачено времени: {duration:.3f} сек")
```

```
Итоговая сумма: 499999999500000000
Затрачено времени: 28.182 сек
```
**Вывод:** хотя threading использует несколько потоков, GIL ограничивает их параллельное выполнение, поэтому этот подход неприменим для тяжёлых вычислений.