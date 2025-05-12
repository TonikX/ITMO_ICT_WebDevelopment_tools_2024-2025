# Задание 1

Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.

## threading

Идея: дать каждому потоку суммировать свой промежуток чисел - при запуске потока, ему в качестве задачи передается calculate_sum с его промежутком, который обновляется для следующего потока. 

Каждый поток получается свою subsum, которая суммируется в глобальную сумму result. 

```python
import threading
import time


result = 0


def calculate_sum(start: int, end: int):
    global result
    subsum = 0
    print(f"{threading.current_thread().name} started summing from {start} to {end}")
    for i in range(start, end + 1):
        subsum += i
    print(f"{threading.current_thread().name} finished. subsum={subsum}")
    result += subsum


if __name__ == "__main__":
    NUM_THREADS = 10
    START = 1
    END = 10**9

    threads = []
    cur_start = 1
    step = END // NUM_THREADS
    cur_end = cur_start + step - 1

    start = time.time()
    for i in range(NUM_THREADS):
        t = threading.Thread(target=calculate_sum, args=(cur_start, cur_end))
        threads.append(t)
        t.start()
        cur_start = cur_end + 1
        cur_end = cur_start + step - 1

    for t in threads:
        t.join()

    print("Final sum=", result)
    print("Done in", time.time() - start, "seconds")
```
Пример вывода: 

```
# NUM_THREADS = 10

Thread-1 (calculate_sum) started summing from 1 to 100000000
Thread-2 (calculate_sum) started summing from 100000001 to 200000000
Thread-3 (calculate_sum) started summing from 200000001 to 300000000
Thread-4 (calculate_sum) started summing from 300000001 to 400000000
Thread-5 (calculate_sum) started summing from 400000001 to 500000000
Thread-6 (calculate_sum) started summing from 500000001 to 600000000
Thread-7 (calculate_sum) started summing from 600000001 to 700000000
Thread-8 (calculate_sum) started summing from 700000001 to 800000000
Thread-9 (calculate_sum) started summing from 800000001 to 900000000
Thread-10 (calculate_sum) started summing from 900000001 to 1000000000
Thread-4 (calculate_sum) finished. subsum=35000000050000000
Thread-6 (calculate_sum) finished. subsum=55000000050000000
Thread-2 (calculate_sum) finished. subsum=15000000050000000
Thread-1 (calculate_sum) finished. subsum=5000000050000000
Thread-9 (calculate_sum) finished. subsum=85000000050000000
Thread-7 (calculate_sum) finished. subsum=65000000050000000
Thread-10 (calculate_sum) finished. subsum=95000000050000000
Thread-8 (calculate_sum) finished. subsum=75000000050000000
Thread-5 (calculate_sum) finished. subsum=45000000050000000
Thread-3 (calculate_sum) finished. subsum=25000000050000000
Final sum= 500000000500000000
Done in 39.592371463775635 seconds
```

```
# NUM_THREADS = 1

Thread-1 (calculate_sum) started summing from 1 to 1000000000
Thread-1 (calculate_sum) finished. subsum=500000000500000000
Final sum= 500000000500000000
Done in 40.29339575767517 seconds
```

## multiprocessing

Идея в целом такая же, как и в threading - разделить весь промежуток на несколько, и дать каждому процессу суммировать его.
Основное отличие заключается в форме передачи промежутков и получение результата:

- pool.map принимает уже готовые промежутки чисел, так что их нужно создать еще до запуска процессов
- pool.map возвращает список результатов функции - подсуммы. Поэтому нужно сложить их, чтобы получить полную сумму.

```python

from multiprocessing import Pool
import time


def calculate_sum(sumrange: tuple[int, int]):
    start, end = sumrange
    subsum = 0
    for i in range(start, end + 1):
        subsum += i
    return subsum


if __name__ == "__main__":
    NUM_PROCESSES = 10
    START = 1
    END = 10**9

    step = END // NUM_PROCESSES
    ranges = []
    for i in range(NUM_PROCESSES):
        cur_start = START + i * step
        cur_end = START + (i + 1) * step - 1
        ranges.append((cur_start, cur_end))

    start = time.time()
    with Pool(processes=NUM_PROCESSES) as pool:
        subsums = pool.map(calculate_sum, ranges)
    fullsum = sum(subsums)
    print("Final sum=", fullsum)
    print("Done in", time.time() - start, "seconds")

```

Пример вывода:
```
# NUM_PROCESSES = 10

Final sum= 500000000500000000
Done in 5.467380046844482 seconds
```
```
# NUM_PROCESSES = 1

Final sum= 500000000500000000
Done in 34.41407608985901 seconds
```

## asyncio

Идея такая же как и раньше - разделяем целый промежуток на части, и создаем задачу для получения суммы этой части. 
Дожидаемся, пока все задачи выполнятся и суммируем результаты.

```python
import asyncio
import time


async def calculate_sum(start: int, end: int):
    subsum = 0
    print(f"Started summing from {start} to {end}")
    for i in range(start, end + 1):
        subsum += i
    print(f"Finished summing from {start} to {end}. subsum={subsum}")
    return subsum


async def main():
    NUM_CORUTINES = 5
    START = 1
    END = 10**9

    step = END // NUM_CORUTINES
    cur_start = START
    cur_end = cur_start + step - 1

    tasks = []

    start = time.time()
    for i in range(NUM_CORUTINES):
        tasks.append(asyncio.create_task(calculate_sum(cur_start, cur_end)))
        cur_start = cur_end + 1
        cur_end = cur_start + step - 1
    subsums = await asyncio.gather(*tasks)
    fullsum = sum(subsums)
    print("Final sum=", fullsum)
    print("Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    asyncio.run(main())
```

```
NUM_CORUTINES = 10

Started summing from 1 to 100000000
Finished summing from 1 to 100000000. subsum=5000000050000000
Started summing from 100000001 to 200000000
Finished summing from 100000001 to 200000000. subsum=15000000050000000
Started summing from 200000001 to 300000000
Finished summing from 200000001 to 300000000. subsum=25000000050000000
Started summing from 300000001 to 400000000
Finished summing from 300000001 to 400000000. subsum=35000000050000000
Started summing from 400000001 to 500000000
Finished summing from 400000001 to 500000000. subsum=45000000050000000
Started summing from 500000001 to 600000000
Finished summing from 500000001 to 600000000. subsum=55000000050000000
Started summing from 600000001 to 700000000
Finished summing from 600000001 to 700000000. subsum=65000000050000000
Started summing from 700000001 to 800000000
Finished summing from 700000001 to 800000000. subsum=75000000050000000
Started summing from 800000001 to 900000000
Finished summing from 800000001 to 900000000. subsum=85000000050000000
Started summing from 900000001 to 1000000000
Finished summing from 900000001 to 1000000000. subsum=95000000050000000
Final sum= 500000000500000000
Done in 41.7538275718689 seconds
```

```
NUM_CORUTINES = 1

Started summing from 1 to 1000000000
Finished summing from 1 to 1000000000. subsum=500000000500000000
Final sum= 500000000500000000
Done in 41.3083233833313 seconds
```

## Сравнение подходов

| Подход          | Время выполнения 1 задачи, c | Время выполнения 10 задач, c |
|-----------------|---------------------------|---------------------------|
| threading       | 40                        | 39                        |
| multiprocessing | 34                        | 5                         |
| asyncio         | 41                        | 41                        |


Вывод:

Задача у нас cpu-bound, поэтому выигрыша у threading и asyncio мы не получили.
 
1. threading как бы параллельно выполняет суммирования промежутков (по выводу консоли видно), но из-за GIL процессор просто быстро переключается между ними, и эффективность такая же, как если бы мы суммировали все в одном потоке.

2. multiprocessing запускает несколько процессов питона, значит CPU дейсвительно может использовать несколько своих ядер. Это дает прирост в производительности. 

3. в asyncio все выполняется в одном потоке, и в самой функции суммирования нет момента, когда можно передать управление другой задачи - поэтому можно считать, что код выполняется как синхронный.

