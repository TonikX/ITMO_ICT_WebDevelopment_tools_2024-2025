# Результаты при ```N=5000000000```

1. Threading

```python
import threading
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

def worker(start, end, results, index):
    results[index] = calculate_sum(start, end)

if __name__ == '__main__':
    N = 5000000000
    num_threads = 4
    chunk_size = N // num_threads
    threads = []
    results = [0] * num_threads

    start_time = time.time()
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_threads - 1 else N
        t = threading.Thread(target=worker, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    end_time = time.time()

    print(f"Threading Total: {total}")
    print(f"Threading Time: {end_time - start_time:.2f} seconds")
```

```python
Threading Total: 12500000002500000000
Threading Time: 51.58 seconds
```

2. Multiprocessing

```python
import multiprocessing
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

if __name__ == '__main__':
    N = 5000000000
    num_processes = 4
    chunk_size = N // num_processes
    ranges = []
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else N
        ranges.append((start, end))

    start_time = time.time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(calculate_sum, ranges)

    total = sum(results)
    end_time = time.time()

    print(f"Multiprocessing Total: {total}")
    print(f"Multiprocessing Time: {end_time - start_time:.2f} seconds")
```
```python
Multiprocessing Total: 12500000002500000000
Multiprocessing Time: 14.10 seconds
```

3. Async
```python
import asyncio
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    N = 5000000000
    num_tasks = 4
    chunk_size = N // num_tasks
    ranges = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else N
        ranges.append((start, end))

    loop = asyncio.get_running_loop()
    start_time = time.time()

    tasks = [loop.run_in_executor(None, calculate_sum, s, e) for s, e in ranges]
    results = await asyncio.gather(*tasks)

    total = sum(results)
    end_time = time.time()

    print(f"Async Total: {total}")
    print(f"Async Time: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    asyncio.run(main())
```
```python
Async Total: 12500000002500000000
Async Time: 50.39 seconds
```

# Вывод:

Наиболее эффективным для ЦПУ задач является мультипроцессинг.