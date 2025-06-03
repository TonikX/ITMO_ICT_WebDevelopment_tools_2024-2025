Результаты выполнения:

| Тип             | Время выполнения, с |
|-----------------|---------------------|
| multithreading  | 9.57                |
| multiprocessing | 2.68                |
| asyncio         | 9.41                |

Версия с multithreading не даёт буста производительности, так как происходит упор
в вычисления с использованием питоновского интерпретатора и параллельное использование
интерпретатора блокируется GIL. Версия с asyncio даёт примерно такой же
результат, так как во-первых всё так же идёт взамиодействие с интерпретатором, а во-вторых
внутри функций вычисления не вызывается await, а значит вся функция выполняется синхронно
в вызывающем потоке. Версия с multiprocessing даёт наибольший буст производительности,
так как в ней создаются реально отдельные процессы, которые могут
параллельно выполняться, так как работают в разных интерпретаторах и не блокируются GIL.
Но есть оверхед на создание процессов.

Во всех 3 реализациях range делится на 33 куска (в случае с процессами на 5), 32 иди 4 из
которых отдаются рабочим потокам или процессам, а последний кусок, остающийся от деления,
суммируется в основном потоке или процессе.

Листинг multithreading:

```python
import threading
import time

def calculate_sum():
    from_value = 1
    to_value = 10**9
    workers_count = 32
    threads = []
    step = (to_value - from_value) // workers_count
    result = [0] * workers_count
    for i in range(workers_count):
        start = from_value + i * step
        end = from_value + (i + 1) * step
        thread = threading.Thread(target = calculate_worker, args = (start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(result) + sum(range(from_value + workers_count * step, to_value + 1))

def calculate_worker(start, end, result, index):
    total = sum(range(start, end))
    result[index] = total

start_time = time.perf_counter()
sum = calculate_sum()
end_time = time.perf_counter()
print(sum)
print(f"{end_time - start_time} seconds")
```

Листинг multiprocessing:

```python
import time
import multiprocessing

def calculate_sum():
    from_value = 1
    to_value = 10 ** 9
    workers_count = 4
    processes = []
    step = (to_value - from_value) // workers_count
    result = multiprocessing.Array('q', workers_count)
    for i in range(workers_count):
        start = from_value + i * step
        end = from_value + (i + 1) * step
        process = multiprocessing.Process(target=calculate_worker, args=(start, end, result, i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    return sum(result) + sum(range(from_value + workers_count * step, to_value + 1))

def calculate_worker(start, end, result, index):
    total = sum(range(start, end))
    result[index] = total

if __name__ == '__main__':
    start_time = time.perf_counter()
    sum = calculate_sum()
    end_time = time.perf_counter()
    print(sum)
    print(f"{end_time - start_time} seconds")
```

Листинг asyncio:

```python
import time
import asyncio

async def calculate_sum():
    from_value = 1
    to_value = 10**9
    workers_count = 32
    tasks = []
    step = (to_value - from_value) // workers_count
    result = [0] * workers_count

    for i in range(workers_count):
        start = from_value + i * step
        end = from_value + (i + 1) * step
        tasks.append(calculate_worker(start, end, result, i))

    await asyncio.gather(*tasks)
    return sum(result) + sum(range(from_value + workers_count * step, to_value + 1))

async def calculate_worker(start, end, result, index):
    total = sum(range(start, end))
    result[index] = total


start_time = time.perf_counter()
sum_result = asyncio.run(calculate_sum())
end_time = time.perf_counter()
print(sum_result)
print(f"{end_time - start_time} seconds")
```