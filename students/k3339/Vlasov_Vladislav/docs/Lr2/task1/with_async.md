Асинхронное решение задачи представляет собой разбиение счётной суммы на равные учатки. Сохдаётся фукция, что считает сумму чисел от start до end.
Создаются несколько задач, каждая из которых получает функцию и промежуток. Все задачи выполняются асинхронно

```
async def calculate(start, end):
    local_sum = 0
    for i in range(start, end):
        local_sum += i
    return local_sum

async def main():

    n = 1000000000
    n_process = multiprocessing.cpu_count()
    n_calculate_one = n // n_process

    start_time = time.perf_counter()
    tasks = []
    for start_calculate in range(0, n, n_calculate_one):
        task = asyncio.create_task(calculate(start_calculate, start_calculate + n_calculate_one))
        tasks.append(task)
    

    results = await asyncio.gather(*tasks)
```