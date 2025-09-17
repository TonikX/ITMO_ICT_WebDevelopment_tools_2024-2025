# Сравнение методов вычисления суммы чисел

В этом проекте рассматриваются три подхода к вычислению суммы чисел от 1 до 100_000_000:

1. **Асинхронный подход (`asyncio`)**
2. **Многопроцессный подход (`multiprocessing`)**
3. **Многопоточный подход (`threading`)**

---

## 1. Асинхронный подход

```python
import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end))

async def main():
    num_tasks = 4
    chunks = 100_000_000 // num_tasks
    start_time = time.time()
    
    tasks = [asyncio.create_task(calculate_sum(i*chunks+1, (i+1)*chunks+1))
             for i in range(num_tasks)]
    
    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    
    print("Async sum:", total_sum)
    print(f"Execution time: {time.time() - start_time} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

Особенности:

Использует asyncio и корутины.

Эффективно при работе с I/O, но не даёт прироста на CPU-bound задачах.

Примерное время выполнения: ~0.79 с.


# 2. Многопроцессный подход
```python
import time
import multiprocessing

def calculate_sum(start, end, result):
    result.append(sum(range(start, end)))

def main():
    num_processes = 4
    chunks = 100_000_000 // num_processes
    start_time = time.time()
    
    manager = multiprocessing.Manager()
    result = manager.list()
    
    processes = [multiprocessing.Process(target=calculate_sum,
                                         args=(i*chunks+1, (i+1)*chunks+1, result))
                 for i in range(num_processes)]
    
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    
    total_sum = sum(result)
    print("Total sum:", total_sum)
    print(f"Execution time: {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()
```


Особенности:

Создаёт отдельные процессы для каждой части задачи.

Хорошо масштабируется на CPU-bound задачах.

Примерное время выполнения: ~0.43 с.



# 3. Многопоточный подход

```python
import time
import threading

def calculate_sum(start, end, result):
    result.append(sum(range(start, end)))

def main():
    num_threads = 4
    chunks = 100_000_000 // num_threads
    start_time = time.time()
    
    result = []
    threads = [threading.Thread(target=calculate_sum,
                                args=(i*chunks+1, (i+1)*chunks+1, result))
               for i in range(num_threads)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    total_sum = sum(result)
    print("Total sum:", total_sum)
    print(f"Execution time: {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()
```

Особенности:

Использует потоки в одном процессе.

Подходит для I/O-bound задач.

На CPU-bound задачах выигрыша нет из-за GIL.

Примерное время выполнения: ~0.90 с

# Выводы
Для CPU-bound задач эффективнее использовать multiprocessing.

Для I/O-bound задач подойдут asyncio или threading.

Все методы дают одинаковый результат: 5000000050000000


