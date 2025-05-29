Многопроцессорное решение задачи представляет собой разбиение счётной суммы на равные учатки. Сохдаётся фукция, что считает сумму чисел от start до end.

Создаются несколько процессов, в соответсвии с числом логических ядер компьютера, на котором запускается задача, каждая из которых получает функцию и промежуток. Все задачи выполняются в разных процессорах

```
def calculate(start, end, results: list):
    local_sum = 0
    for i in range(start, end):
        local_sum += i
    results.append(local_sum)


if __name__ == "__main__":

    n = 1000000000
    n_process = multiprocessing.cpu_count()
    print(n_process)

    n_calculate_one = n // n_process

    start_time = time.perf_counter()

    manager = multiprocessing.Manager()
    results = manager.list()
    processes: list[multiprocessing.Process] = []

    for start_calculate in range(0, n, n_calculate_one):
        process = multiprocessing.Process(target=calculate, args=(start_calculate, start_calculate + n_calculate_one, results))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
```

Данные записываются в общую переменную - список, а потом объединяются