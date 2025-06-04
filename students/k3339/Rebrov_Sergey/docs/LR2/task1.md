## **Задание**

Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 1.000.000.000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.
 
## **Таблица**

| Метод              | Время      | Комментарий                                                         |
|--------------------|------------|---------------------------------------------------------------------|
| `threading`        | 30.43 сек  | Почти не даёт прироста производительности                           |
| `multiprocessing`  | 6.97 сек   | Существенно быстрее за счёт использования нескольких процессов      |
| `asyncio`          | 72.56 сек  | Асинхронность не даёт преимущества, так как задача не связана с I/O |


## **Файлы**

`threading_pr.py`
```python
def calculate_sum(total=10 ** 9, num_threads=32):
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        start = i * step
        end = total if i == num_threads - 1 else (i + 1) * step
        thread = threading.Thread(target=partial_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)
```

`multiprocessing_pr.py`
```python
def calculate_sum(total=10 ** 9, num_processes=32):
    step = total // num_processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        tasks = [(i * step, total if i == num_processes - 1 else (i + 1) * step) for i in range(num_processes)]
        results = pool.starmap(partial_sum, tasks)
    return sum(results)
```

`async_pr.py`
```python
async def calculate_sum(total=10 ** 9, num_parts=4):
    step = total // num_parts
    tasks = [
        partial_sum(i * step, total if i == num_parts - 1 else (i + 1) * step)
        for i in range(num_parts)
    ]
    results = await asyncio.gather(*tasks)
    return sum(results)
```